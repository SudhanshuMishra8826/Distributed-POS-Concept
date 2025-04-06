require('dotenv').config();
const { Kafka } = require('kafkajs');
const Redis = require('redis');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

// Import utils from parent directory
const utilsPath = path.join(__dirname, '..', 'utils.js');
const { checkPluginStatus, logPluginInactive } = require(utilsPath);

// Plugin ID
const PLUGIN_ID = 'purchase-recommender';

// Define recommendation rules
const recommendationRules = [
    {
        // If a customer buys bread, recommend butter
        condition: (itemId) => itemId && itemId.includes('bread'),
        recommendation: { name: 'Butter', price: 2.99, category: 'Dairy' }
    },
    {
        // If a customer buys milk, recommend cereal
        condition: (itemId) => itemId && itemId.includes('milk'),
        recommendation: { name: 'Cereal', price: 4.99, category: 'Breakfast' }
    },
    {
        // If a customer buys coffee, recommend creamer
        condition: (itemId) => itemId && itemId.includes('coffee'),
        recommendation: { name: 'Coffee Creamer', price: 3.49, category: 'Beverages' }
    },
    {
        // If a customer buys pasta, recommend sauce
        condition: (itemId) => itemId && itemId.includes('pasta'),
        recommendation: { name: 'Pasta Sauce', price: 3.99, category: 'Condiments' }
    },
    {
        // If a customer buys chips, recommend dip
        condition: (itemId) => itemId && itemId.includes('chips'),
        recommendation: { name: 'Dip', price: 2.49, category: 'Snacks' }
    }
];

// Default recommendation to show when no specific rules match
const defaultRecommendation = {
    name: 'Store Special',
    price: 5.99,
    category: 'Promotion',
    description: 'Our store special of the week!'
};

class PurchaseRecommender {
    constructor() {
        // Initialize Kafka
        this.kafka = new Kafka({
            clientId: 'purchase-recommender',
            brokers: (process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:9092').split(',')
        });

        // Initialize Kafka consumer
        this.consumer = this.kafka.consumer({
            groupId: 'purchase-recommender-group',
            fromBeginning: true
        });

        // Initialize Kafka producer
        this.producer = this.kafka.producer();

        // Initialize Redis client
        this.redisClient = Redis.createClient({
            url: `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`
        });

        // Connect to Redis
        this.redisClient.connect().catch(console.error);

        // Track basket history
        this.basketHistory = new Map();
    }

    async start() {
        console.log('Starting Purchase Recommender plugin...');

        // Connect to Kafka
        await this.consumer.connect();
        await this.producer.connect();

        // Subscribe to topics
        await this.consumer.subscribe({
            topics: ['pos_events'],
            fromBeginning: true
        });

        // Start consuming messages
        await this.consumer.run({
            eachMessage: async ({ topic, partition, message }) => {
                try {
                    const event = JSON.parse(message.value.toString());
                    await this.processEvent(event);
                } catch (error) {
                    console.error('Error processing message:', error);
                }
            }
        });
    }

    async processEvent(event) {
        // Check if the plugin is active
        const isActive = await checkPluginStatus(PLUGIN_ID);
        if (!isActive) {
            logPluginInactive(PLUGIN_ID, event);
            return;
        }

        const { event_type, basket_id, item_id, quantity, price } = event;

        if (event_type === 'item_added') {
            await this.handleItemAdded(basket_id, item_id, quantity, price);
        }
    }

    async handleItemAdded(basket_id, item_id, quantity, price) {
        try {
            console.log(`Item added to basket ${basket_id}: item_id=${item_id}, quantity=${quantity}, price=${price}`);

            // Create an item object for storage
            const item = {
                id: item_id,
                quantity: quantity,
                price: price
            };

            // Get basket history from Redis
            let basketItems = await this.redisClient.get(`basket:${basket_id}`);
            basketItems = basketItems ? JSON.parse(basketItems) : [];

            // Ensure basketItems is an array
            if (!Array.isArray(basketItems)) {
                basketItems = [];
            }

            // Add new item to basket history
            basketItems.push(item);

            // Save updated basket history to Redis
            await this.redisClient.set(`basket:${basket_id}`, JSON.stringify(basketItems));

            // Generate recommendations based on the current item
            const recommendations = this.generateRecommendations(item_id, basketItems);

            if (recommendations.length > 0) {
                // Publish recommendations event
                await this.producer.send({
                    topic: 'pos_recommendations',
                    messages: [
                        {
                            key: basket_id,
                            value: JSON.stringify({
                                event_type: 'recommendations',
                                basket_id,
                                recommendations,
                                timestamp: new Date().toISOString()
                            })
                        }
                    ]
                });

                console.log(`Published recommendations for basket ${basket_id}:`, recommendations);
            }
        } catch (error) {
            console.error('Error handling item added:', error);
            // Continue processing other events even if this one fails
        }
    }

    generateRecommendations(currentItemId, basketItems) {
        const recommendations = [];
        let hasSpecificRecommendation = false;

        // Check each recommendation rule
        for (const rule of recommendationRules) {
            if (rule.condition(currentItemId)) {
                hasSpecificRecommendation = true;
                // Check if the recommended item is already in the basket
                const alreadyInBasket = basketItems.some(
                    item => item && item.id && item.id.toLowerCase() === rule.recommendation.name.toLowerCase()
                );

                if (!alreadyInBasket) {
                    recommendations.push(rule.recommendation);
                }
            }
        }

        // Add default recommendation if no specific recommendations were found
        if (!hasSpecificRecommendation && basketItems.length > 0) {
            // Check if the default recommendation is already in the basket
            const alreadyInBasket = basketItems.some(
                item => item && item.id && item.id.toLowerCase() === defaultRecommendation.name.toLowerCase()
            );

            if (!alreadyInBasket) {
                recommendations.push(defaultRecommendation);
            }
        }

        // Add dynamic recommendations based on basket history
        // This is a simple example - in a real system, you might use machine learning
        if (basketItems.length >= 3) {
            // If basket has 3 or more items, recommend a discount
            recommendations.push({
                name: 'Special Discount',
                price: 0,
                category: 'Promotion',
                discount: '10% off your next purchase'
            });
        }

        return recommendations;
    }

    async stop() {
        console.log('Stopping Purchase Recommender plugin...');
        await this.consumer.disconnect();
        await this.producer.disconnect();
        await this.redisClient.quit();
    }
}

// Start the plugin
const recommender = new PurchaseRecommender();

// Handle graceful shutdown
process.on('SIGINT', async () => {
    await recommender.stop();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    await recommender.stop();
    process.exit(0);
});

recommender.start().catch(console.error); 