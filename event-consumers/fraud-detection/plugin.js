#!/usr/bin/env node

/**
 * Fraud Detection Plugin
 * 
 * This plugin monitors payment events from the POS system and detects high-value transactions.
 */

require('dotenv').config();
const { Kafka } = require('kafkajs');
const Redis = require('ioredis');
const { v4: uuidv4 } = require('uuid');
const { checkPluginStatus, logPluginInactive } = require('../utils');

// Configure logging
const log = {
    info: (message) => console.log(`[INFO] ${new Date().toISOString()} - ${message}`),
    warn: (message) => console.log(`[WARN] ${new Date().toISOString()} - ${message}`),
    error: (message) => console.log(`[ERROR] ${new Date().toISOString()} - ${message}`),
    debug: (message) => console.log(`[DEBUG] ${new Date().toISOString()} - ${message}`)
};

// Plugin ID
const PLUGIN_ID = 'fraud-detection';

class FraudDetectionPlugin {
    constructor() {
        // Initialize Kafka client
        this.kafka = new Kafka({
            clientId: `fraud-detection-${uuidv4()}`,
            brokers: (process.env.KAFKA_BROKER || 'localhost:9092').split(',')
        });

        // Initialize Kafka consumer and producer
        this.consumer = this.kafka.consumer({ groupId: 'fraud-detection-group' });
        this.producer = this.kafka.producer();

        // Initialize Redis client
        this.redis = new Redis({
            host: process.env.REDIS_HOST || 'localhost',
            port: parseInt(process.env.REDIS_PORT || '6379'),
            password: process.env.REDIS_PASSWORD || '',
            keyPrefix: 'fraud:'
        });

        // Configuration
        this.highValueThreshold = 10; // Alert for transactions over $10
        this.running = true;

        // Set up signal handlers
        process.on('SIGINT', this.handleShutdown.bind(this));
        process.on('SIGTERM', this.handleShutdown.bind(this));
    }

    async handleShutdown() {
        log.info('Shutting down...');
        this.running = false;
        await this.close();
        process.exit(0);
    }

    async start() {
        try {
            // Connect to Kafka
            await this.consumer.connect();
            await this.producer.connect();

            // Subscribe to the topic
            await this.consumer.subscribe({
                topic: 'pos_events',
                fromBeginning: false
            });

            log.info('Fraud Detection Plugin started');

            // Start consuming messages
            await this.consumeMessages();
        } catch (error) {
            log.error(`Error starting plugin: ${error.message}`);
            await this.close();
            process.exit(1);
        }
    }

    async consumeMessages() {
        try {
            await this.consumer.run({
                eachMessage: async ({ topic, partition, message }) => {
                    try {
                        const event = JSON.parse(message.value.toString());
                        await this.processEvent(event);
                    } catch (error) {
                        log.error(`Error processing message: ${error.message}`);
                    }
                }
            });
        } catch (error) {
            log.error(`Error in consumer loop: ${error.message}`);
            if (this.running) {
                setTimeout(() => this.consumeMessages(), 5000);
            }
        }
    }

    async processEvent(event) {
        try {
            // Check if the plugin is active
            const isActive = await checkPluginStatus(PLUGIN_ID);
            if (!isActive) {
                logPluginInactive(PLUGIN_ID, event);
                return;
            }

            // Log every valid event
            log.info(`Received event: ${JSON.stringify(event)}`);

            const { event_type, customer_id, basket_id, amount } = event;
            const customerKey = customer_id || 'anonymous';
            const basketKey = basket_id || 'unknown';

            // Check if it's a payment_processed event
            if (event_type === 'payment_completed') {
                log.info(`Processing payment_processed event for basket ${basketKey}`);

                // Check if amount is higher than threshold
                const paymentAmount = parseFloat(amount);

                if (paymentAmount > this.highValueThreshold) {
                    log.info(`High value transaction detected: $${paymentAmount} for basket ${basketKey}`);
                    await this.createHighValueAlert(customerKey, basketKey, paymentAmount, event);
                } else {
                    log.info(`Normal transaction: $${paymentAmount} for basket ${basketKey}`);
                }
            } else {
                log.info(`Skipping non-payment event: ${event_type}`);
            }
        } catch (error) {
            log.error(`Error processing event: ${error.message}`);
            log.error(`Event that caused error: ${JSON.stringify(event)}`);
        }
    }

    async createHighValueAlert(customerId, basketId, amount, event) {
        try {
            const alert = {
                event_type: 'fraud_alert',
                alert_id: uuidv4(),
                customer_id: customerId,
                basket_id: basketId,
                rule_id: 'high-value-transaction',
                rule_name: 'High Value Transaction',
                rule_description: 'Detects transactions with unusually high values',
                severity: 'medium',
                action: 'alert',
                amount: amount,
                threshold: this.highValueThreshold,
                timestamp: new Date().toISOString(),
                original_event: {
                    event_type: event.event_type,
                    timestamp: event.timestamp
                }
            };

            await this.producer.send({
                topic: 'pos_events',
                messages: [{ key: alert.alert_id, value: JSON.stringify(alert) }]
            });

            log.info(`High value alert created for basket ${basketId}`);
        } catch (error) {
            log.error(`Error creating alert: ${error.message}`);
        }
    }

    async close() {
        try {
            await this.consumer.disconnect();
            await this.producer.disconnect();
            await this.redis.quit();
            log.info('Connections closed');
        } catch (error) {
            log.error(`Error closing connections: ${error.message}`);
        }
    }
}

// Start the plugin
const plugin = new FraudDetectionPlugin();
plugin.start().catch(error => {
    log.error(`Fatal error: ${error.message}`);
    process.exit(1);
}); 