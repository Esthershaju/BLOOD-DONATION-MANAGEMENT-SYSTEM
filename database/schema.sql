-- Blood Donation Management System
-- Database Schema Definition & Initial Seed Data

CREATE DATABASE IF NOT EXISTS blood_donation_db;
USE blood_donation_db;

-- 1. Table: hospitals
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table: donors
CREATE TABLE IF NOT EXISTS donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    last_donation_date DATE NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table: blood_inventory
CREATE TABLE IF NOT EXISTS blood_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group VARCHAR(5) NOT NULL UNIQUE,
    units INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Table: blood_requests
CREATE TABLE IF NOT EXISTS blood_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    units INT NOT NULL,
    urgency ENUM('Normal', 'Urgent', 'Critical') NOT NULL DEFAULT 'Normal',
    status ENUM('Pending', 'Processing', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hospital FOREIGN KEY (hospital_id) 
        REFERENCES hospitals(hospital_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- Seed Initial Data
-- -------------------------------------------------------------

-- Seed Blood Inventory for all 8 standard groups
INSERT INTO blood_inventory (blood_group, units) VALUES
('A+', 14),
('A-', 6),
('B+', 18),
('B-', 5),
('AB+', 9),
('AB-', 3),
('O+', 22),
('O-', 8)
ON DUPLICATE KEY UPDATE units=VALUES(units);

-- Seed Hospitals
INSERT INTO hospitals (hospital_name, city, phone) VALUES
('City General Hospital', 'Mumbai', '022-24101000'),
('Apex Trauma & Surgical Care', 'Pune', '020-25678900'),
('Metropolitan Blood & Research Center', 'Mumbai', '022-26543210'),
('LifeLine Specialty Hospital', 'Navi Mumbai', '022-27894561'),
('Global Heart & Kidney Institute', 'Thane', '022-25348970'),
('St. Jude Children & Community Hospital', 'Pune', '020-26123456')
ON DUPLICATE KEY UPDATE hospital_name=VALUES(hospital_name);

-- Seed Donors
INSERT INTO donors (name, age, gender, blood_group, phone, email, city, available, last_donation_date) VALUES
('Aarav Sharma', 26, 'Male', 'O+', '9876543210', 'aarav.sharma@example.com', 'Mumbai', 1, '2024-01-15'),
('Priya Patel', 24, 'Female', 'A+', '9876543211', 'priya.patel@example.com', 'Pune', 1, '2024-02-10'),
('Rohan Mehta', 31, 'Male', 'B+', '9876543212', 'rohan.mehta@example.com', 'Mumbai', 1, '2023-11-20'),
('Ananya Deshmukh', 22, 'Female', 'O-', '9876543213', 'ananya.d@example.com', 'Thane', 1, '2024-03-01'),
('Vikram Joshi', 35, 'Male', 'AB+', '9876543214', 'vikram.j@example.com', 'Pune', 0, '2024-04-05'),
('Neha Kulkarni', 29, 'Female', 'A-', '9876543215', 'neha.k@example.com', 'Navi Mumbai', 1, '2023-12-18'),
('Siddharth Rao', 28, 'Male', 'B-', '9876543216', 'siddharth.r@example.com', 'Mumbai', 1, '2024-02-28'),
('Tanvi Verma', 27, 'Female', 'AB-', '9876543217', 'tanvi.v@example.com', 'Pune', 1, '2024-01-22'),
('Aditya Nair', 42, 'Male', 'O+', '9876543218', 'aditya.n@example.com', 'Thane', 0, '2024-03-14'),
('Sneha Shinde', 23, 'Female', 'B+', '9876543219', 'sneha.s@example.com', 'Mumbai', 1, '2024-02-05')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Seed Blood Requests
INSERT INTO blood_requests (hospital_id, blood_group, units, urgency, status, requested_at) VALUES
(1, 'O-', 3, 'Critical', 'Pending', NOW() - INTERVAL 120 MINUTE),
(2, 'A+', 4, 'Urgent', 'Pending', NOW() - INTERVAL 90 MINUTE),
(3, 'B+', 2, 'Normal', 'Pending', NOW() - INTERVAL 60 MINUTE),
(1, 'AB+', 2, 'Urgent', 'Processing', NOW() - INTERVAL 45 MINUTE),
(4, 'O+', 5, 'Critical', 'Completed', NOW() - INTERVAL 300 MINUTE)
ON DUPLICATE KEY UPDATE units=VALUES(units);
