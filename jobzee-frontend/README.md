# JobZee Frontend

A modern Next.js 14 frontend application for the JobZee Job Application System with internationalization support.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Internationalization**: next-intl
- **UI Components**: Headless UI + Heroicons
- **Package Manager**: npm

## Supported Languages

- English (en)
- Hindi (hi)
- Spanish (es)
- French (fr)
- Malayalam (ml)
- Turkish (tr)
- Gujarati (gu)
- Bengali (bn)
- Arabic (ar)
- Russian (ru)
- Marathi (mr)
- Kannada (kn)

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd jobzee-frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

### Docker

```bash
# Build Docker image
docker build -t jobzee-frontend .

# Run container
docker run -p 3000:3000 jobzee-frontend
```

## Project Structure

```
├── app/                    # Next.js App Router
│   ├── [locale]/          # Internationalized routes
│   └── i18n.ts           # i18n configuration
├── components/            # Reusable UI components
│   └── ui/               # Base UI components
├── hooks/                # Custom React hooks
├── locales/              # Translation files
│   ├── en.json          # English translations
│   ├── hi.json          # Hindi translations
│   └── ...              # Other languages
├── public/               # Static assets
└── styles/               # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_APP_NAME=JobZee Job System
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
