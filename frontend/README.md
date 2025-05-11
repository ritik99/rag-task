# RAG System Frontend

This is a [Next.js](https://nextjs.org) application serving as the frontend interface for the RAG (Retrieval Augmented Generation) system. It allows users to interact with the backend API to upload documents, ask questions, and view responses.

This project was bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Project Structure

The frontend is organized as follows:

-   `app/`: The core directory for Next.js using the App Router.
    -   `page.tsx`: The main page component for the application interface.
    -   `layout.tsx`: The main layout component for the application.
    -   `globals.css`: Global styles for the application.
    -   `favicon.ico`: The application's favicon.
-   `components/`: Contains reusable React components.
    -   `ui/`: Likely contains UI elements built with a library like Shadcn/UI (e.g., `button.tsx`, `card.tsx`).
-   `lib/`: Contains utility functions and type definitions.
    -   `types.ts`: TypeScript type definitions used across the frontend.
    -   `utils.ts`: Utility functions.
-   `public/`: Stores static assets like images and icons (e.g., `next.svg`, `vercel.svg`).
-   `next.config.ts`: Configuration file for Next.js.
-   `package.json`: Defines project metadata, scripts, and dependencies.
-   `tsconfig.json`: TypeScript configuration for the project.

## Getting Started

### Prerequisites

-   Node.js (version recommended by Next.js, typically latest LTS)
-   `bun`, `npm`, `yarn`, or `pnpm` as a package manager.
-   The backend API server must be running (see `../backend/README.md` for instructions). By default, the frontend expects the backend to be available at `http://localhost:8000`.

### Running the Development Server

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    Choose one of the following based on your preferred package manager:
    ```bash
    bun install
    # or
    npm install
    # or
    yarn install
    # or
    pnpm install
    ```

3.  **Run the development server:**
    ```bash
    bun run dev
    # or
    npm run dev
    # or
    yarn dev
    # or
    pnpm dev
    ```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the main page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

### Backend API Connection

The frontend application needs to communicate with the backend API. By default, it assumes the backend is running at `http://localhost:8000/api/v1`.

If your backend is running on a different URL or port, you will need to configure this in the frontend. This is typically done via an environment variable. For example, you might create a `.env.local` file in the `frontend` directory with the following content:

```
NEXT_PUBLIC_API_BASE_URL=http://your-backend-host:your-backend-port/api/v1
```

Then, update the frontend code where API calls are made to use this environment variable.

## Key Features (Implemented or Planned)

-   **Document Upload:** Interface to upload text or PDF files to the backend.
-   **Query Interface:** Allow users to submit questions to the RAG system.
-   **Results Display:** Show the answers and source documents retrieved by the RAG system.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

-   [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
-   [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
