# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import pymysql

app = Flask(__name__)
app.secret_key = 'super_secret_key'
bcrypt = Bcrypt(app)

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='WJ28@krhps',
        database='library_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('library'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            
            cursor.execute("INSERT INTO MEMBER (name, email, join_date) VALUES (%s, %s, CURDATE())", (username, email))
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash('Email already exists or error occurred.', 'danger')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('library'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/library')
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT author_id, name, country FROM AUTHOR")
    authors = cursor.fetchall()
    conn.close()
    return render_template('index.html', authors=authors, username=session.get('username'))

@app.route('/search_books', methods=['GET'])
def search_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.args.get('title', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    if min_price is not None and min_price < 0:
        min_price = 0.0
    if max_price is not None and max_price < 0:
        max_price = 0.0
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT book_id, title, price FROM BOOK WHERE 1=1"
    params = []
    
    if title:
        query += " AND title LIKE %s"
        params.append(f"%{title}%")
        
    if min_price is not None:
        query += " AND price >= %s"
        params.append(min_price)
        
    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)
        
    query += " ORDER BY price ASC"
        
    cursor.execute(query, tuple(params))
    books = cursor.fetchall()
    
    conn.close()
    
    return render_template('search_books.html', books=books)

@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    error_message = None
    
    if request.method == 'POST':
        author_name = request.form.get('name', '').strip()
        country = request.form.get('country', '').strip()
        book_title = request.form.get('book_title', '').strip()
        publish_year = request.form.get('publish_year', type=int)
        price = request.form.get('price', type=float)
        category_name = request.form.get('category_name', '').strip()
        publisher_name = request.form.get('publisher_name', '').strip()
        
        if publish_year and publish_year > 2026:
            error_message = "Publish year cannot be greater than 2026!"
        elif price is not None and price < 0:
            error_message = "Price cannot be negative!"
        elif author_name and country:
            category_id = 1
            if category_name:
                cursor.execute("SELECT category_id FROM CATEGORY WHERE LOWER(name) = LOWER(%s)", (category_name,))
                cat_res = cursor.fetchone()
                if cat_res:
                    category_id = cat_res['category_id'] if isinstance(cat_res, dict) else cat_res[0]
                else:
                    cursor.execute("INSERT INTO CATEGORY (name) VALUES (%s)", (category_name,))
                    conn.commit()
                    cursor.execute("SELECT LAST_INSERT_ID() AS category_id")
                    new_cat = cursor.fetchone()
                    category_id = new_cat['category_id'] if isinstance(new_cat, dict) else new_cat[0]

            publisher_id = 1
            if publisher_name:
                cursor.execute("SELECT publisher_id FROM PUBLISHER WHERE LOWER(name) = LOWER(%s)", (publisher_name,))
                pub_res = cursor.fetchone()
                if pub_res:
                    publisher_id = pub_res['publisher_id'] if isinstance(pub_res, dict) else pub_res[0]
                else:
                    cursor.execute("INSERT INTO PUBLISHER (name, country) VALUES (%s, %s)", (publisher_name, country))
                    conn.commit()
                    cursor.execute("SELECT LAST_INSERT_ID() AS publisher_id")
                    new_pub = cursor.fetchone()
                    publisher_id = new_pub['publisher_id'] if isinstance(new_pub, dict) else new_pub[0]

            cursor.execute("""
                SELECT author_id FROM AUTHOR 
                WHERE LOWER(name) = LOWER(%s) AND LOWER(country) = LOWER(%s)
            """, (author_name, country))
            existing_author = cursor.fetchone()
            
            if existing_author:
                author_id = existing_author['author_id'] if isinstance(existing_author, dict) else existing_author[0]
                if book_title:
                    cursor.execute("""
                        INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (book_title, price if price is not None else 0.00, publish_year if publish_year else 2026, author_id, publisher_id, category_id))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('library'))
                else:
                    error_message = "This author from the same country already exists!"
            else:
                cursor.execute("""
                    INSERT INTO AUTHOR (name, country) 
                    VALUES (%s, %s)
                """, (author_name, country))
                conn.commit()
                
                if book_title:
                    cursor.execute("SELECT LAST_INSERT_ID() AS author_id")
                    res = cursor.fetchone()
                    author_id = res['author_id'] if isinstance(res, dict) else res[0]
                    
                    cursor.execute("""
                        INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (book_title, price if price is not None else 0.00, publish_year if publish_year else 2026, author_id, publisher_id, category_id))
                    conn.commit()
                
                conn.close()
                return redirect(url_for('library'))
                
    cursor.execute("SELECT author_id, name, country FROM AUTHOR")
    authors_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('authors.html', authors_list=authors_list, error_message=error_message)

@app.route('/add_author', methods=['POST'])
def add_author():
    return redirect(url_for('authors'))

@app.route('/catalogue')
def catalogue():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.book_id, b.title, b.price, b.publish_year, 
               a.name AS author_name, p.name AS publisher_name, c.name AS category_name
        FROM BOOK b
        JOIN AUTHOR a ON b.author_id = a.author_id
        JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
        JOIN CATEGORY c ON b.category_id = c.category_id
        ORDER BY b.book_id ASC
    """)
    books = cursor.fetchall()
    conn.close()
    return render_template('catalogue.html', books=books)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price', type=float)
        publish_year = request.form.get('publish_year', type=int)
        author_id = request.form.get('author_id')
        publisher_id = request.form.get('publisher_id')
        category_id = request.form.get('category_id')
        
        if price is not None and price < 0:
            price = 0.0
        if publish_year and publish_year > 2026:
            publish_year = 2026
            
        cursor.execute("""
            UPDATE BOOK 
            SET title = %s, price = %s, publish_year = %s, author_id = %s, publisher_id = %s, category_id = %s 
            WHERE book_id = %s
        """, (title, price, publish_year, author_id, publisher_id, category_id, book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('catalogue'))
        
    cursor.execute("SELECT * FROM BOOK WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    
    cursor.execute("SELECT author_id, name FROM AUTHOR")
    authors = cursor.fetchall()
    
    cursor.execute("SELECT publisher_id, name FROM PUBLISHER")
    publishers = cursor.fetchall()
    
    cursor.execute("SELECT category_id, name FROM CATEGORY")
    categories = cursor.fetchall()
    
    conn.close()
    return render_template('edit_book.html', book=book, authors=authors, publishers=publishers, categories=categories)

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BOOK WHERE book_id = %s", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalogue'))

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.name AS category_name, COUNT(b.book_id) AS book_count, AVG(b.price) AS avg_price
        FROM CATEGORY c
        LEFT JOIN BOOK b ON c.category_id = b.category_id
        GROUP BY c.category_id, c.name
    """)
    cat_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT a.name, COUNT(b.book_id) AS book_count
        FROM AUTHOR a
        JOIN BOOK b ON a.author_id = b.author_id
        GROUP BY a.author_id, a.name
        HAVING COUNT(b.book_id) >= 2
    """)
    pro_authors = cursor.fetchall()
    
    cursor.execute("""
        SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price
        FROM BOOK
    """)
    price_stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('reports.html', 
                           cat_stats=cat_stats, 
                           pro_authors=pro_authors,
                           price_stats=price_stats)

@app.route('/loans')
def loans_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date 
        FROM LOAN l
        JOIN BOOK b ON l.book_id = b.book_id
        JOIN MEMBER m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL
    """)
    active_loans = cursor.fetchall()
    
    cursor.execute("""
        SELECT m.member_id, m.name, m.email 
        FROM MEMBER m
        WHERE m.member_id NOT IN (
            SELECT member_id FROM LOAN WHERE return_date IS NULL
        )
    """)
    available_members = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.book_id, b.title 
        FROM BOOK b
        WHERE b.book_id NOT IN (
            SELECT book_id FROM LOAN WHERE return_date IS NULL
        )
    """)
    available_books = cursor.fetchall()
    
    conn.close()
    
    return render_template('loans.html', 
                           active_loans=active_loans, 
                           available_members=available_members, 
                           available_books=available_books)

@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    error_message = None
    
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        loan_date = request.form.get('loan_date')
        
        if loan_date and loan_date > '2026-11-17':
            error_message = "Loan date cannot be after the year 2026!"
        else:
            cursor.execute("""
                SELECT * FROM LOAN 
                WHERE book_id = %s AND member_id = %s AND return_date IS NULL
            """, (book_id, member_id))
            existing_loan = cursor.fetchone()
            
            if existing_loan:
                error_message = "This member already has an active loan for this book and hasn't returned it yet!"
            else:
                cursor.execute("""
                    INSERT INTO LOAN (book_id, member_id, loan_date) 
                    VALUES (%s, %s, %s)
                """, (book_id, member_id, loan_date))
                conn.commit()
                conn.close()
                return redirect(url_for('loans_management'))
        
    cursor.execute("SELECT book_id, title FROM BOOK")
    books = cursor.fetchall()
    
    cursor.execute("SELECT member_id, name FROM MEMBER")
    members = cursor.fetchall()
    conn.close()
    
    return render_template('add_loan.html', books=books, members=members, error_message=error_message)

@app.route('/return_loan/<int:loan_id>')
def return_loan(loan_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE LOAN SET return_date = CURDATE() WHERE loan_id = %s", (loan_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('loans_management'))

@app.route('/most_borrowed')
def most_borrowed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.title, COUNT(l.loan_id) AS loan_count
        FROM LOAN l
        JOIN BOOK b ON l.book_id = b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY loan_count DESC
        LIMIT 3
    """)
    top_books = cursor.fetchall()
    
    cursor.execute("""
        SELECT m.name, COUNT(l.loan_id) AS total_loans
        FROM LOAN l
        JOIN MEMBER m ON l.member_id = m.member_id
        GROUP BY m.member_id, m.name
        ORDER BY total_loans DESC
        LIMIT 1
    """)
    active_member = cursor.fetchone()
    
    conn.close()
    
    return render_template('most_borrowed.html', top_books=top_books, active_member=active_member)

@app.route('/authors_books')
def authors_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
        FROM AUTHOR a
        LEFT JOIN BOOK b ON a.author_id = b.author_id
        GROUP BY a.author_id, a.name
    """)
    author_counts = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.title AS book_title, a.name AS author_name, p.name AS publisher_name, a.country
        FROM BOOK b
        JOIN AUTHOR a ON b.author_id = a.author_id
        JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
        WHERE a.country = p.country
    """)
    matching_books = cursor.fetchall()
    
    conn.close()
    
    return render_template('authors_books.html', 
                           author_counts=author_counts, 
                           matching_books=matching_books)

@app.route('/edit_author/<int:author_id>', methods=['GET', 'POST'])
def edit_author(author_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        country = request.form['country']
        cursor.execute("UPDATE AUTHOR SET name = %s, country = %s WHERE author_id = %s", (name, country, author_id))
        conn.commit()
        conn.close()
        return redirect(url_for('library'))
        
    cursor.execute("SELECT * FROM AUTHOR WHERE author_id = %s", (author_id,))
    author = cursor.fetchone()
    conn.close()
    return render_template('edit_author.html', author=author)

@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AUTHOR WHERE author_id = %s", (author_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('library'))

if __name__ == '__main__':
    app.run(debug=True)