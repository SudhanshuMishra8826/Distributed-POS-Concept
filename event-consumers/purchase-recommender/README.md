# Purchase Recommender Plugin

This plugin detects item addition events from the POS system and makes recommendations for additional items based on predefined rules and basket history.

## Features

- Listens to `pos_events` topic for item addition events
- Stores basket history in Redis for persistence
- Generates recommendations based on:
  - Predefined rules (e.g., if bread is added, recommend butter)
  - Default recommendations for items with no specific rules
  - Basket history (e.g., if 3+ items are in the basket, offer a discount)
- Publishes recommendations to the `pos_recommendations` topic

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

Start the plugin:
```bash
npm start
```

## Recommendation Rules

The plugin includes the following hard-coded recommendation rules:

- If a customer buys bread, recommend butter
- If a customer buys milk, recommend cereal
- If a customer buys coffee, recommend creamer
- If a customer buys pasta, recommend sauce
- If a customer buys chips, recommend dip

Additionally, the plugin offers:
- A default "Store Special" recommendation for items with no specific rules
- A 10% discount promotion when a basket contains 3 or more items

## Extending Recommendation Rules

To add new recommendation rules, edit the `recommendationRules` array in `plugin.js`.

To modify the default recommendation, edit the `defaultRecommendation` object in `plugin.js`.

## Testing

Run tests:
```bash
npm test
``` 