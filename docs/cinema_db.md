# Cinema application database setup

### Creating the database

```
CREATE DATABASE IF NOT EXISTS `cinema`;
```
```
USE cinema;
```

<br />
<br />
<br />

### Creating tables

* Staff

```
CREATE TABLE IF NOT EXISTS Staff (
    username VARCHAR(30) NOT NULL,
    pswd VARCHAR(50) NOT NULL,
    role ENUM('salesman', 'manager'),

    PRIMARY KEY(username)
);
```

* Customers

```
CREATE TABLE IF NOT EXISTS Customers (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    phoneNumber CHAR(9),
    email VARCHAR(50),
    n_tickets INT,

    PRIMARY KEY(id)
);

ALTER TABLE Customers AUTO_INCREMENT = 0;
```

* Languages

```
CREATE TABLE IF NOT EXISTS Languages (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    type ENUM('Original', 'Subtitles', 'Voiceover', 'Dubbing') NOT NULL,

    PRIMARY KEY(id)
);
```

* Movies

```
CREATE TABLE IF NOT EXISTS Movies (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(50) NOT NULL,
    length INT NOT NULL CHECK(length > 0),
    language_id INT NOT NULL CHECK(language_id > 0),

    PRIMARY KEY(id),

    CONSTRAINT fk_language
        FOREIGN KEY(language_id)
        REFERENCES Languages(id)
);
```

* Rooms

```
CREATE TABLE IF NOT EXISTS Rooms (
    id INT NOT NULL AUTO_INCREMENT,
    s_max INT NOT NULL CHECK(s_max > 0),

    PRIMARY KEY(id)
);
```

* Schedule

```
CREATE TABLE IF NOT EXISTS Schedule (
    id INT NOT NULL AUTO_INCREMENT,
    movie_id INT NOT NULL CHECK(movie_id > 0),
    room_id INT NOT NULL CHECK(room_id > 0),
    start_time DATETIME NOT NULL,
    s_taken INT NOT NULL CHECK(s_taken >= 0),

    PRIMARY KEY(id),

    CONSTRAINT fk_movie
        FOREIGN KEY(movie_id)
        REFERENCES Movies(id),

    CONSTRAINT fk_room
        FOREIGN KEY(room_id)
        REFERENCES Rooms(id)
);
```

* Tickets

```
CREATE TABLE IF NOT EXISTS Tickets (
    id INT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL CHECK(customer_id >= 0),
    schedule_id INT NOT NULL CHECK(schedule_id > 0),
    ticket_price INT NOT NULL CHECK(ticket_price > 0),
    n_seats INT NOT NULL CHECK(n_seats > 0),

    PRIMARY KEY(id),

    CONSTRAINT fk_customer
        FOREIGN KEY(customer_id)
        REFERENCES Customers(id),

    CONSTRAINT fk_schedule
        FOREIGN KEY(schedule_id)
        REFERENCES Schedule(id)
);
```

<br />
<br /> 
<br />

### Adding procedures and triggers

* Movie overlap checking ???

```
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS checkMovieOverlap (movie INT, room INT, start DATETIME)
BEGIN
    DECLARE overlap_count INT DEFAULT 0;
    DECLARE movie_length INT DEFAULT 0;

    SET movie_length = (SELECT length FROM Movies WHERE id = movie);

    SELECT COUNT(s.id) 
        FROM Schedule AS s JOIN Movies AS m ON s.movie_id = m.id
        WHERE room_id = room
            AND DATE(s.start_time) = DATE(start)
            AND DATE_ADD(s.start_time, INTERVAL m.length MINUTE) BETWEEN
                start AND DATE_ADD(s.start_time, INTERVAL movie_length MINUTE);
        INTO overlap_count;

    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Movie overlap';
    END IF;
END$$
DELIMITER ;
```

```
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS movieOverlapInsert
    BEFORE INSERT
    ON Schedule
    FOR EACH ROW

    BEGIN
        DECLARE overlap_count INT DEFAULT 0;
        DECLARE movie_length INT DEFAULT 0;

        SET movie_length = (SELECT length FROM Movies WHERE id = NEW.movie_id);

        SELECT COUNT(s.id) 
            FROM Schedule AS s JOIN Movies AS m ON s.movie_id = m.id
            WHERE id = NEW.id 
                AND room_id = NEW.room_id
                AND DATE(s.start_time) = DATE(NEW.start_time)
                AND DATE_ADD(s.start_time, INTERVAL m.length MINUTE) 
                    BETWEEN NEW.start_time AND DATE_ADD(s.start_time, INTERVAL movie_length MINUTE);
            INTO overlap_count;

        IF overlap_count > 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Movie overlap';
        END IF;
    END$$
DELIMITER ;
```

<br />

* Update taken steats count and handle max seats overflow when adding a new ticket

```
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS updateTakenSeats (schedule_id INT, n_seats_old INT, n_seats_new INT)
BEGIN
    DECLARE s_taken, s_max INT DEFAULT 0;
    SET s_taken = (SELECT s_taken FROM Schedule WHERE id = schedule_id);
    SET s_max = (SELECT max_seats 
                        FROM Schedule AS s JOIN Rooms AS r ON s.room_id = r.id
                        WHERE s.id = schedule_id);
    
    IF s_taken - n_seats_old + n_seats_new > s_max THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Seat number overflow';
    END IF;

    UPDATE Schedule 
        SET taken_seats = taken_seats - n_seats_old + n_seats_new 
        WHERE id = schedule_id;
END $$
DELIMITER ;
```

```
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS takenSeatsInsert
    BEFORE INSERT
    ON Tickets
    FOR EACH ROW

    BEGIN
        CALL updateTakenSeats(NEW.schedule_id, 0, NEW.n_seats);
    END$$
DELIMITER ;
```

```
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS takenSeatsUpdate
    BEFORE UPDATE
    ON Tickets
    FOR EACH ROW

    BEGIN
        CALL updateTakenSeats(NEW.schedule_id, OLD.n_seats, NEW.n_seats);
    END$$
DELIMITER ;
```

```
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS takenSeatsDelete
    AFTER DELETE
    ON Tickets
    FOR EACH ROW

    BEGIN
        CALL updateTakenSeats(OLD.schedule_id, OLD.n_seats, 0);
    END$$
DELIMITER ;
```

<br />
<br />
<br />

### Creating database users

* Initial user

```
CREATE USER IF NOT EXISTS 'init'@'localhost';
SET PASSWORD FOR 'init'@'localhost' = PASSWORD(<password>);
GRANT SELECT ON cinema.Staff TO 'init'@'localhost';
FLUSH PRIVILEGES;
```

<br />

* Salesman

```
CREATE USER IF NOT EXISTS 'salesman'@'localhost';
SET PASSWORD FOR 'salesman'@'localhost' = PASSWORD(<password>);
GRANT SELECT ON cinema.Movies TO 'salesman'@'localhost';
GRANT SELECT ON cinema.Schedule TO 'salesman'@'localhost';
GRANT SELECT, INSERT ON cinema.Customers TO 'salesman'@'localhost';
GRANT SELECT, INSERT ON cinema.Tickets TO 'salesman'@'localhost';
FLUSH PRIVILEGES;
```

<br />

* Manager

```
CREATE USER IF NOT EXISTS 'manager'@'localhost';
SET PASSWORD FOR 'manager'@'localhost' = PASSWORD(<password>);
GRANT SELECT, UPDATE, INSERT ON cinema.Staff ON 'manager'@'localhost';
GRANT SELECT, UPDATE, INSERT ON cinema.Movies TO 'salesman'@'localhost';
GRANT SELECT, UPDATE, INSERT ON cinema.Schedule TO 'salesman'@'localhost';
GRANT SELECT, UPDATE, INSERT ON cinema.Customers TO 'salesman'@'localhost';
GRANT SELECT, UPDATE, INSERT ON cinema.Tickets TO 'salesman'@'localhost';
FLUSH PRIVILEGES;
```