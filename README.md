# 🚆 Railway Ticket Reservation API  

A **Django-based** Railway Ticket Reservation system that manages **ticket booking, RAC allocation, and waiting lists** while enforcing **berth constraints and concurrency handling**.  

## 📌 Features  
- **Berth Allocation:** Automatically assigns available berths based on priority rules.  
- **RAC Management:** Allocates RAC (Reservation Against Cancellation) slots when confirmed berths are full.  
- **Waitlist Handling:** Places passengers on the waitlist if RAC is also full.  
- **Priority Rules:**  
   - Senior citizens (60+) and ladies with children get priority for lower berths.  
   - RAC passengers are assigned side-lower berths.  
- **Concurrency Handling:** Ensures no overbooking using database transactions.  
- **REST API Endpoints:** Supports **booking, cancellation, and ticket status retrieval**.  
- **Dockerized Deployment:** Run the entire application seamlessly with Docker.  

## 🏗 Architecture Diagram  

Below is the architecture diagram for the Railway Ticket Reservation API:

```plaintext
+-----------------------+
|    Client (Browser)   |
+-----------------------+
         |
         v
+-----------------------+
|  REST API Endpoints   |
|  (Django Framework)   |
+-----------------------+
         |
         v
+-----------------------+
|  Business Logic Layer |
| (Berth Allocation,    |
|  RAC, Waitlist, etc.) |
+-----------------------+
         |
         v
+-----------------------+
|  Database Layer       |
|     (SQLite)          |
+-----------------------+
         |
         v
+-----------------------+
|  Dockerized Services  |
| (App + DB Containers) |
+-----------------------+
```

### Key Components:
1. **Client (Browser):** Users interact with the system through a web interface or API clients.
2. **REST API Endpoints:** Django-based endpoints handle requests for booking, cancellation, and ticket status.
3. **Business Logic Layer:** Implements berth allocation, RAC, waitlist management, and concurrency handling.
4. **Database Layer:** Stores passenger details, ticket statuses, and berth availability using SQLite.
5. **Dockerized Services:** Ensures seamless deployment and scalability with Docker Compose.

---

## 🚀 Quick Start (Using Docker)  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/prajwalr16/RailwayTicketReservation.git
cd RailwayTicketReservation
```

### 2️⃣ Build and Run the Docker Container  
```bash
sudo docker-compose up -d --build
sudo docker-compose up -d
```

The Docker container will automatically set up the database, create an admin user, and initialize the berths.

### 3️⃣ Access the Web App  
- Open your browser and visit:  
   [http://localhost:8000/](http://localhost:8000/)  

- To access the Django Admin Panel, use:  
   [http://localhost:8000/admin/](http://localhost:8000/admin/)  

   **Credentials:**  
   - Username: `admin`  
   - Password: `admin`  

---

## 📖 API Endpoints  

### 1. Book a Ticket  
**Endpoint:** `POST /api/v1/tickets/book`  
**Request Body:**  
```json
{
   "passenger": {
      "name": "Ramesh",
      "age": 28,
      "gender": "male",
      "child_under_5": false
   }
}
```

**Responses:**  
- **Success (Confirmed Ticket):**  
   ```json
   {
      "message": "Ticket booked successfully",
      "ticket_id": 123,
      "berth_type": "lower"
   }
   ```
- **Allocated to RAC:**  
   ```json
   {
      "message": "Added to RAC",
      "ticket_id": 456,
      "berth_type": "side-lower"
   }
   ```
- **Waitlist Full (No Tickets Available):**  
   ```json
   {
      "error": "No tickets available"
   }
   ```

---

### 2. Cancel a Ticket  
**Endpoint:** `DELETE /api/v1/tickets/cancel/{ticket_id}`  
**Response:**  
```json
{
   "message": "Ticket cancelled successfully",
   "ticket_id": 123
}
```

---

### 3. View Booked Tickets  
**Endpoint:** `GET /api/v1/tickets/booked`  
**Response:**  
```json
{
   "tickets": [
      {
         "ticket_id": 1,
         "passenger": "Ramesh",
         "berth_type": "lower",
         "status": "confirmed"
      },
      {
         "ticket_id": 2,
         "passenger": "Suresh",
         "berth_type": "side-lower",
         "status": "RAC"
      }
   ]
}
```

---

### 4. View Available Tickets  
**Endpoint:** `GET /api/v1/tickets/available`  
**Response:**  
```json
{
   "confirmed_berths_available": 4,
   "rac_slots_available": 18,
   "waitlist_slots_available": 10
}
```

---


🛑 **Stopping the Application**  
To stop the running Docker containers:  
```bash
sudo docker-compose down
```

---

## 🛠 Development Setup (Optional)  

If you want to run the project without Docker, follow these steps:

### 1️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 2️⃣ Apply Migrations  
```bash
python3 manage.py makemigrations  
python3 manage.py migrate  
```

### 3️⃣ Run the Django Server  
```bash
python3 manage.py runserver
```

The application will be available at [http://localhost:8000/](http://localhost:8000/).