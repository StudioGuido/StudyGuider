## Getting Started (Docker Setup)

Make sure you have **Docker** installed.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/StudyGuider.git
cd StudyGuider
```

### 2. Build and Start All Services
This command builds and starts the frontend, backend, and database containers:

`docker-compose up --build`

### 3. Stop and Remove Containers
To stop everything and remove all associated volumes (like cached DB data):

`docker-compose down -v`
