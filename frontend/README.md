# Frontend - React.js Application

This is the frontend for the Delivery Driver Management & Route Optimization System, built with React.js and Tailwind CSS.

## Features

-   **Dashboard**: Overview of drivers and orders.
-   **Orders**: List of all orders with their assignment status.
-   **Routes**: Details of all available routes.
-   **Optimization**: Trigger the order assignment optimization and view the results, including workload distribution charts.

## Setup and Run Locally

1.  **Navigate to the frontend directory**:
    ```bash
    cd delivery-driver-system/frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run the application**:
    ```bash
    npm start
    ```
    The frontend will be available at `http://localhost:3000`.

## Configuration

The frontend communicates with the backend API. The base URL for the API can be configured via the `REACT_APP_API_BASE_URL` environment variable. By default, it points to `http://localhost:8000`.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.

You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.
