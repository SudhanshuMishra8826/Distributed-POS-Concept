# Plugin Manager Frontend

A Next.js application for managing plugins in the Distributed POS system.

## Features

- View all plugins
- Create new plugins
- Edit existing plugins
- Toggle plugin status (active/inactive)
- Delete plugins

## Technologies Used

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios
- React Hook Form
- React Hot Toast

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd Distributed-POS-Concept/frontend
   ```

3. Install dependencies:
   ```
   npm install
   # or
   yarn install
   ```

4. Start the development server:
   ```
   npm run dev
   # or
   yarn dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`. Make sure the backend service is running before using the frontend.

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js app router
│   │   ├── create/           # Create plugin page
│   │   ├── edit/             # Edit plugin page
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Home page
│   ├── components/           # React components
│   │   ├── Header.tsx        # Header component
│   │   ├── PluginCard.tsx    # Plugin card component
│   │   └── PluginForm.tsx    # Plugin form component
│   ├── lib/                  # Utility functions
│   │   └── api.ts            # API service
│   └── types/                # TypeScript types
│       └── plugin.ts         # Plugin types
├── public/                   # Static assets
├── next.config.js            # Next.js configuration
├── package.json              # Dependencies
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── tsconfig.json             # TypeScript configuration
```

## License

This project is licensed under the MIT License. 