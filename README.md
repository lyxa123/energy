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

## Troubleshooting

### If you see either of these errors in your terminal:

```
exec: "/app/start.sh": permission denied
```
or
```
exec /app/start.sh: no such file or directory
```

It means the `start.sh` file doesn't have execute permissions. Here's how to fix it:

1. **On Windows:** Use Git to set the permissions:

   ```bash
   git update-index --chmod=+x start.sh
   ```

2. **On macOS/Linux:** Run this command in the project folder:

   ```bash
   chmod +x start.sh
   ```

3. Then rebuild the image:

   ```bash
   docker compose build
   ```

**What to Expect:** After running these commands, the container should start without permission errors.have to worry about complicated setup or installations.

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

> **Zoom Controls:** The simulation window might not perfectly fit your browser. Here are ways to zoom in/out:
> - **noVNC Toolbar**: Look for the small toolbar on the left side of the VNC window - it has zoom controls (select Settings>Scaling Mode: local scale)
> - **Right-click Menu**: Right-click anywhere in the VNC window and look for "Scaling" or "Zoom" options  
> - **Browser Menu**: Use your browser's main menu (≡ button) → Zoom instead of keyboard shortcuts
> - **Mouse Wheel**: Try `Ctrl` + mouse wheel while **not** clicking inside the VNC window

## How It All Works (The Magic Explained)

Curious about what's happening in the background? Here’s a simple breakdown:

-   **Docker:** Think of Docker as creating a mini, self-contained computer inside your main computer. This mini-computer has the perfect operating system and all the specific software needed to run the Energy Simulator, so it works reliably every time.
-   **Xvfb (X Virtual Framebuffer):** Since the Docker container doesn't have a physical monitor, we create a "virtual screen" for the application to draw on. This is what `Xvfb` does.
-   **x11vnc & noVNC:** These two tools work together like a webcam pointed at the virtual screen. `x11vnc` captures what the application is drawing, and `noVNC` streams it directly to your web browser, allowing you to see and interact with the simulation as if it were running natively on your machine.

This setup might seem complex, but it's all automated through the Docker configuration and the provided scripts. You get a fully functional simulation environment with just a few simple commands!

---

## Additional Setup for Linux Users

If you're using Linux and running into strange errors like `ContainerConfig` issues or permission denied messages, this section is for you! Docker Compose on Linux sometimes requires a little extra setup compared to macOS or Windows. Most Linux distributions come with an outdated version of Docker Compose (`v1.x`), which can cause compatibility issues with this project. You’ll want to upgrade to the newer Compose v2.

### Use Docker Compose v2

1. First, check if you already have Docker Compose v2:

   ```bash
   docker compose version
   ```

   If this command fails or shows a version below `v2`, continue with the steps below.

2. Install `curl` if it's not already available:

   ```bash
   sudo apt update
   sudo apt install curl
   ```

3. Create the directory for Docker CLI plugins:

   ```bash
   mkdir -p ~/.docker/cli-plugins
   ```

4. Download the latest Docker Compose v2 binary:

   ```bash
   curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
   ```

5. Make the file executable:

   ```bash
   chmod +x ~/.docker/cli-plugins/docker-compose
   ```

6. Verify the installation:

   ```bash
   docker compose version
   ```

   **What to Expect:** You should see something like `Docker Compose version v2.27.0`. 

>  **Important:** Use `docker compose` with a space for this version, not `docker-compose` with a dash.

7. Restart the simulator:

   ```bash
   docker compose up --build
   ```

---

### Additional Errors: Making Sure `start.sh` is Executable

If you see this error in your terminal:

```
exec: "/app/start.sh": permission denied
```

It means the `start.sh` file doesn’t have execute permissions. Here's how to fix it:

1. Run the following command in the project folder:

   ```bash
   chmod +x start.sh
   ```

2. Then rebuild the image:

   ```bash
   docker compose build
   ```

---

### Additional Errors: Removing Old or Conflicting Containers

If you encounter an error like:

```
The container name "..._energy-sim" is already in use
```

It just means Docker is trying to reuse a container that already exists. You can clean it up like this:

Remove any old containers:

   ```bash
   docker container prune -f
   ```

---

## Project Structure

The Energy City Simulator uses a modular architecture for better maintainability:

```
energy/
├── pyPSA_db.py              # Main application entry point
├── constants.py             # Shared constants and settings
├── config_manager.py        # Configuration management
├── entities/                # Power system entities
│   ├── __init__.py
│   ├── base_entity.py      # Base Entity class
│   ├── power_station.py    # PowerStation implementation
│   └── power_consumer.py   # PowerConsumer implementation
├── graphics/                # Graphics and UI components
│   ├── __init__.py
│   ├── renderer_3d.py      # 3D isometric rendering
│   ├── color_manager.py    # Color management and themes
│   ├── ui_components.py    # UI components (buttons, panels, etc.)
│   ├── layout_manager.py   # Screen layout management
│   └── visual_effects.py   # Visual effects and animations
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_entities.py    # Entity tests
│   ├── test_power_station.py
│   ├── test_power_consumer.py
│   └── test_graphics.py    # Graphics module tests
├── run_tests.py            # Test runner script
└── assets/                 # Images and resources
```

## Development and Testing

To run the test suite locally (requires Python environment setup):

```bash
# Run all tests
python run_tests.py

# Run specific test file
python run_tests.py tests/test_entities.py

# Run with verbose output
python run_tests.py -v
```

The project includes comprehensive test coverage:
- **83 total tests** across all modules
- Entity framework tests (11 tests)
- Power station functionality tests (9 tests)  
- Power consumer functionality tests (13 tests)
- Graphics and UI component tests (50 tests)

---
