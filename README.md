# Lab Inventory Management System

A modern, mobile-friendly Django application for managing laboratory inventory, tracking stock levels, and generating/scanning QR codes for efficient workflows.

## 🚀 Features

- **Dashboard**: Real-time overview of inventory status and low stock alerts.
- **Item Management**: Full CRUD operations for lab items with SKU/Barcode support.
- **QR Code Integration**: Automatic QR code generation for every item.
- **Mobile QR Scanner**: Built-in scanner to quickly lookup and manage items using a smartphone camera.
- **Stock Tracking**: Log all check-ins, check-outs, and manual adjustments.
- **Categories & Locations**: Organize items by type and storage location.

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd labinv
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   Copy `.env.example` to `.env` and fill in your details (e.g., SECRET_KEY, DEBUG, etc.):
   ```bash
   cp .env.example .env
   ```

4. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (to access the admin panel):

   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

   *For mobile access, run:* `python manage.py runserver 0.0.0.0:8000`

## 📱 Mobile Workflow

This app is designed to be used on the go:

- Access the `QR Scanner` from the main menu.
- Point your camera at a generated QR code.
- Instantly view item details or log a transaction (Check-In/Out).

## 🗄️ Project Structure

- `inventory/`: Core application logic, models, and views.
- `labinv/`: Project configuration and settings.
- `templates/`: HTML templates (Mobile-first design).
- `static/`: CSS and JavaScript assets.
- `media/`: Generated QR codes and uploaded images.

### System Version

Built with Django 5.0.14
