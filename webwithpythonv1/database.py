import sqlite3

def init_db():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    # Tạo bảng users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tạo bảng subjects
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Tạo bảng questions
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            type TEXT NOT NULL,  -- 'multiple_choice', 'short_answer', 'essay'
            content TEXT NOT NULL,
            options TEXT,  -- JSON string for multiple choice options
            keywords TEXT,  -- Keywords for short_answer/essay
            correct_answer TEXT,  -- For multiple_choice
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    ''')

    # Tạo bảng results
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject_id INTEGER,
            score INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    ''')

    # Thêm dữ liệu mẫu
    c.execute("INSERT OR IGNORE INTO subjects (name) VALUES ('Toán'), ('Văn'), ('Anh')")
    c.execute('''
        INSERT OR IGNORE INTO questions (subject_id, type, content, options, keywords, correct_answer)
        VALUES
        (1, 'multiple_choice', '2 + 2 = ?', '["2", "3", "4", "5"]', NULL, '4'),
        (1, 'short_answer', 'Thủ đô của Việt Nam là gì?', NULL, 'Hà Nội', NULL),
        (1, 'essay', 'Giải thích tại sao 1 + 1 = 2', NULL, 'cộng, số học, kết quả', NULL)
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()