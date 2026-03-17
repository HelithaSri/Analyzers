
# Analyzers

A collection of lightweight analysis tools for logs, database queries, and performance troubleshooting.

Currently includes three main analyzer modules:

- **log-analyzer** → General log file parsing, filtering, and visualization
- **p6spy_analyzer** → Tools to process and analyze P6Spy JDBC log output (SQL query logging)
- **slow-query-analyzer** → Detection, aggregation, and reporting of slow database queries

## 📂 Project Structure

```
Analyzers/
├── log-analyzer/           # Log parsing & analysis tools
├── p6spy_analyzer/         # P6Spy log analyzer (SQL timing, frequency, etc.)
├── slow-query-analyzer/    # Slow query log processor (MySQL, PostgreSQL, etc.)
├── README.md
└── .DS_Store              
```

## 🎯 Purpose

This repository gathers small, focused utilities I built while debugging performance issues in web applications and databases.  
Main use-cases:

- Finding the most frequent / slowest SQL queries
- Understanding application behavior through log files
- Turning raw P6Spy output into actionable insights

## 🛠️ Technologies

- **Python** – core logic & data processing
- **HTML + JavaScript** – simple reports / visualizations (when included)
- Tested mainly with logs from Java/Spring applications + MySQL/PostgreSQL

  
## 📊 Example Use Cases

- **P6Spy** → `spy.log` files → top 20 slowest queries + count by SQL pattern
- **Slow query log** → MySQL slow log → aggregated report with execution time histograms
- **Application logs** → error rate over time, most common exceptions, etc.

## ⚙️ Contributing

Found a bug? Have an idea for a new analyzer?  
Feel free to open an issue or submit a pull request.

---

⭐ If any of these tools helped you debug faster – consider giving the repo a star!
