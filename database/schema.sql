CREATE DATABASE IF NOT EXISTS ai_resume_builder;
USE ai_resume_builder;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL DEFAULT '',
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(100) NOT NULL DEFAULT 'Untitled Resume',
  template VARCHAR(20) NOT NULL DEFAULT 'modern',
  target_role VARCHAR(150) DEFAULT '',
  full_name VARCHAR(150) DEFAULT '',
  email VARCHAR(255) DEFAULT '',
  phone VARCHAR(50) DEFAULT '',
  location VARCHAR(150) DEFAULT '',
  website VARCHAR(255) DEFAULT '',
  github VARCHAR(255) DEFAULT '',
  linkedin VARCHAR(255) DEFAULT '',
  summary TEXT,
  objective TEXT,
  score INT DEFAULT NULL,
  category VARCHAR(50) DEFAULT NULL,
  confidence DECIMAL(6,2) DEFAULT NULL,
  evaluated_at DATETIME DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_resume_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS education (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resume_id INT NOT NULL,
  institution VARCHAR(255) DEFAULT '',
  degree VARCHAR(150) DEFAULT '',
  field_of_study VARCHAR(255) DEFAULT '',
  level VARCHAR(50) DEFAULT 'Bachelor''s',
  start_year VARCHAR(10) DEFAULT '',
  end_year VARCHAR(10) DEFAULT '',
  grade VARCHAR(50) DEFAULT '',
  CONSTRAINT fk_education_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experience (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resume_id INT NOT NULL,
  company VARCHAR(255) DEFAULT '',
  role VARCHAR(150) DEFAULT '',
  start_year VARCHAR(10) DEFAULT '',
  end_year VARCHAR(50) DEFAULT '',
  responsibilities TEXT,
  CONSTRAINT fk_experience_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resume_id INT NOT NULL,
  skill VARCHAR(100) DEFAULT '',
  description TEXT,
  CONSTRAINT fk_skill_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resume_id INT NOT NULL,
  project_name VARCHAR(150) DEFAULT '',
  tech_stack VARCHAR(255) DEFAULT '',
  relevance INT DEFAULT 0,
  description TEXT,
  CONSTRAINT fk_project_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  resume_id INT NOT NULL,
  certification VARCHAR(255) DEFAULT '',
  issuer VARCHAR(255) DEFAULT '',
  year VARCHAR(10) DEFAULT '',
  CONSTRAINT fk_cert_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);
