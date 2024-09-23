# Ping Latency Bot

## Project Description
This bot measures Maplestory servers' latency over the past 5 minutes and aggregates the average ping and standard deviation across 40 servers. It helps users monitor server performance and utilizes the information to their advantage by playing on stable channels.

![me](https://github.com/Alexny1992/latency_bot/blob/master/check_ping.gif)
![me](https://github.com/Alexny1992/latency_bot/blob/master/ping_graph.gif)

- **Technologies Used**: 
  - Python for bot development
  - PostgreSQL for data storage
  - Discord API for interaction
  - Git for version control

- **Challenges Faced**:
  - [x] Handling multiple channel pings simultaneously
  - [x] Ensuring accurate data aggregation
  - [x] Connecting with Discord API to ensure it's running
  - [x] Connecting with PostgreSQL through psycopg2 to ensure data injection properly
  - [x] Managing Discord API rate limits to avoid being banned
  - [x] Implementing robust error handling for API timeouts and database issues
  - [x] Ensuring thread safety during concurrent pings to avoid race conditions
  - [x] Managing thread lifecycle and performance, especially with many channels
  - [x] Propagating errors from threads back to the main execution flow
  - [x] Implementing timeout handling to prevent hanging threads
  - [x] Outputting images of past 5 minutes of ping data for a selected channel and displaying them through Matplotlib
    
- **Next Step**: 
  - [ ] Deploy the project to the cloud to ensure it runs 24/7, allowing users to access real-time ping data.
  - [ ] Integrate Apache Kafka for streamlining information flow, enabling real-time data processing and messaging between components.
  - [ ] Develop a web interface or dashboard for users to visualize ping statistics and access historical data.
  - [ ] Implement user authentication and authorization to control access to the bot's features.
  - [ ] Set up automated testing to ensure reliability and maintainability of the codebase.
  - [ ] Explore additional data analytics features, such as generating reports or trends based on latency over time.
    
- **Libraries Used**
  - Matplotlib
  - Numpy
  - Pandas
  - Treading
  - Tcp_latency
  - Tabulate
  - Postgres
  - discord
  - Asyncio
  - OS


