USE library_db;

INSERT INTO AUTHOR (name, country) VALUES 
('Naguib Mahfouz', 'Egypt'),
('Tawfiq al-Hakim', 'Egypt'),
('Taha Hussein', 'Egypt'),
('William Shakespeare', 'UK');

INSERT INTO PUBLISHER (name, country) VALUES 
('Dar Al Shorouk', 'Egypt'),
('Dar Al Maaref', 'Egypt'),
('Penguin Books', 'UK');

INSERT INTO CATEGORY (name) VALUES 
('Novels'), 
('History'), 
('Science & Tech');

INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) VALUES 
('Midaq Alley', 18.50, 1947, 1, 1, 1),
('Palace Walk', 22.00, 1956, 1, 1, 1),
('The People of the Cave', 14.00, 1933, 2, 2, 1),
('Bird of the East', 16.50, 1938, 2, 1, 1),
('Intro to AI', 35.00, 2023, 3, 2, 3),
('Modern History of Egypt', 25.00, 2015, 3, 1, 2),
('Unborrowed Novel', 19.00, 2020, 3, 2, 1),
('Data Science Basics', 12.00, 2021, 1, 3, 3),
('World War II', 28.00, 2022, 2, 2, 2),
('Advanced Python', 40.00, 2024, 3, 3, 3);

INSERT INTO MEMBER (name, email, join_date) VALUES 
('Ahmed Mohamed', 'ahmed@gmail.com', '2025-01-10'),
('Sara Ali', 'sara@gmail.com', '2025-02-15'),
('Mahmoud Hassan', 'mahmoud@gmail.com', '2025-03-01'),
('Mona Ibrahim', 'mona@gmail.com', '2025-04-12'),
('Karim Youssef', 'karim@gmail.com', '2025-05-20');

INSERT INTO LOAN (book_id, member_id, loan_date, return_date) VALUES 
(1, 1, '2026-01-01', '2026-01-10'),
(2, 2, '2026-01-05', '2026-01-15'),
(3, 3, '2026-02-01', '2026-02-10'),
(4, 4, '2026-02-03', '2026-02-13'),
(5, 1, '2026-03-01', '2026-03-10'),
(6, 2, '2026-03-05', '2026-03-15'),
(8, 3, '2026-04-01', '2026-04-10'),
(9, 4, '2026-04-05', '2026-04-15'),
(1, 2, '2026-05-01', '2026-05-10'),
(2, 3, '2026-05-05', '2026-05-15'),
(3, 1, '2026-06-01', '2026-06-10'),
(4, 2, '2026-06-15', NULL);