# Energy Simulator

Welcome to the Energy Simulator! This project runs in a self-contained environment using Docker, so you don't have to worry about complicated setup or installations.

## Prerequisites

Before you begin, make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (This is usually included with Docker Desktop)

## Getting Started

Follow these steps to get the simulation up and running.

### Step 1: Start the Simulation

First, we'll build the environment and start the application.

1.  Open a terminal or command prompt in the project's main directory.
2.  Run the following command:
    ```bash
    docker-compose up --build
    ```
    **What to Expect:** You will see a lot of text scroll by in your terminal. This is normal! Docker is downloading the necessary components and setting up the environment for the first time. You'll see messages about packages being installed and the container being created.

    The process is successful when the terminal output stops scrolling and you see log messages from the application, such as `pygame... Hello from the pygame community` and `The VNC desktop is...`. This means the simulation is running inside the container.

### Step 2: View in Your Browser

Now that the simulation is running, you can view it in your web browser.

1.  Open your favorite web browser (like Chrome, Firefox, or Edge).
2.  Navigate to this address: **[http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)**
3.  You will see a screen with the **noVNC** logo and a **Connect** button. Click it.

### Step 3: Interact with the Simulation

After clicking "Connect," you should see the Energy Simulator application interface inside your browser window.

> **Tip:** The simulation window might not perfectly fit your browser. You can use your browser's built-in zoom controls (`Ctrl` and `+` or `-` on Windows/Linux, `Cmd` and `+` or `-` on Mac) to resize the view to your liking.

## How It All Works (The Magic Explained)

Curious about what's happening in the background? Here’s a simple breakdown:

-   **Docker:** Think of Docker as creating a mini, self-contained computer inside your main computer. This mini-computer has the perfect operating system and all the specific software needed to run the Energy Simulator, so it works reliably every time.
-   **Xvfb (X Virtual Framebuffer):** Since the Docker container doesn't have a physical monitor, we create a "virtual screen" for the application to draw on. This is what `Xvfb` does.
-   **x11vnc & noVNC:** These two tools work together like a webcam pointed at the virtual screen. `x11vnc` captures what the application is drawing, and `noVNC` streams it directly to your web browser, allowing you to see and interact with the simulation as if it were running natively on your machine.

This setup might seem complex, but it's all automated through the Docker configuration and the provided scripts. You get a fully functional simulation environment with just a few simple commands!
