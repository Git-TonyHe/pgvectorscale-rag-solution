# Building a High-Performance RAG Solution with Pgvectorscale and Python

This tutorial guides you through setting up and using `pgvectorscale` with Docker and Python, leveraging **Infini-AI's bge-m3 model** for embeddings. You'll build a cutting-edge RAG (Retrieval-Augmented Generation) solution, combining advanced retrieval techniques (including hybrid search) with intelligent answer generation based on retrieved context. Perfect for AI engineers looking to enhance their projects with state-of-the-art vector search and generation capabilities using PostgreSQL.

## YouTube Tutorial
You can watch the full tutorial here on [YouTube](https://youtu.be/hAdEuDBN57g).

## Pgvectorscale Documentation

For more information about using PostgreSQL as a vector database in AI applications with Timescale, check out these resources:

- [GitHub Repository: pgvectorscale](https://github.com/timescale/pgvectorscale)
- [Blog Post: PostgreSQL and Pgvector: Now Faster Than Pinecone, 75% Cheaper, and 100% Open Source](https://www.timescale.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost/)
- [Blog Post: RAG Is More Than Just Vector Search](https://www.timescale.com/blog/rag-is-more-than-just-vector-search/)
- [Blog Post: A Python Library for Using PostgreSQL as a Vector Database in AI Applications](https://www.timescale.com/blog/a-python-library-for-using-postgresql-as-a-vector-database-in-ai-applications/)

## Why PostgreSQL?

Using PostgreSQL with pgvectorscale as your vector database offers several key advantages over dedicated vector databases:

- PostgreSQL is a robust, open-source database with a rich ecosystem of tools, drivers, and connectors. This ensures transparency, community support, and continuous improvements.

- By using PostgreSQL, you can manage both your relational and vector data within a single database. This reduces operational complexity, as there's no need to maintain and synchronize multiple databases.

- Pgvectorscale enhances pgvector with faster search capabilities, higher recall, and efficient time-based filtering. It leverages advanced indexing techniques, such as the DiskANN-inspired index, to significantly speed up Approximate Nearest Neighbor (ANN) searches.

Pgvectorscale Vector builds on top of [pgvector](https://github.com/pgvector/pgvector), offering improved performance and additional features, making PostgreSQL a powerful and versatile choice for AI applications.

## Prerequisites

- Docker
- Python 3.7+
- **Infini-AI API key** (sign up at [Infini-AI](https://cloud.infini-ai.com))
- PostgreSQL GUI client (optional, e.g., TablePlus, DBeaver, or psql CLI)

## Steps

1. Set up Docker environment
2. Connect to the database using a PostgreSQL GUI client
3. Create a Python script to insert document chunks as vectors using bge-m3 embeddings
4. Create a Python function to perform similarity search

## Detailed Instructions

### 1. Set up Docker environment

The project includes a `docker-compose.yml` file in the `docker/` directory:

```yaml
services:
  timescaledb:
    image: timescale/timescaledb-ha:pg16
    container_name: timescaledb
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  timescaledb_data:
```

Run the Docker container:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Connect to the database

You can connect using any PostgreSQL client:

- **Host**: 127.0.0.1 (use this instead of localhost on some systems)
- **Port**: 5432
- **User**: postgres
- **Password**: password
- **Database**: postgres

### 3. Configure environment variables

Copy the example environment file and update it:

```bash
cp app/example.env app/.env
```

Edit `app/.env` and add your Infini-AI API key:

```env
# Database configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password

# Infini-AI configuration
INFINI_API_KEY=your_infini_ai_api_key_here
INFINI_BASE_URL=https://cloud.infini-ai.com/maas/v1
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSIONS=1024
LLM_MODEL=deepseek-ai/DeepSeek-V3
```

### 4. Install Python dependencies

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 5. Insert vectors into the database

Run the vector insertion script:

```bash
python app/insert_vectors.py
```

This script will:
- Load FAQ data from `data/faq_dataset.csv`
- Generate embeddings using the bge-m3 model (1024 dimensions)
- Insert vectors into the PostgreSQL database

### 6. Perform similarity searches

Run the similarity search script:

```bash
python app/similarity_search.py
```

This script demonstrates:
- Basic similarity search
- Metadata filtering
- Time-based filtering
- LLM-powered response generation

## Project Structure

```
.
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration and environment loading
│   ├── database/
│   │   ├── connect_postgres.py  # Database connection utilities
│   │   └── vector_store.py      # Vector store operations
│   ├── services/
│   │   ├── llm_factory.py       # LLM client factory
│   │   └── synthesizer.py       # Response synthesis
│   ├── insert_vectors.py        # Insert vectors into database
│   └── similarity_search.py     # Perform similarity searches
├── data/
│   └── faq_dataset.csv          # Sample FAQ data
├── docker/
│   └── docker-compose.yml       # Docker configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Key Features

### 1. **Vector Search with Metadata Filtering**
   - Search by semantic similarity
   - Filter by metadata (e.g., category, date)
   - Time-range filtering for temporal data

### 2. **LLM-Powered Response Generation**
   - Uses Infini-AI's DeepSeek-V3 model
   - Context-aware answer synthesis
   - Thought process transparency

### 3. **High-Performance Indexing**
   - Timescale Vector's DiskANN-inspired index
   - Optimized for large-scale vector datasets
   - Efficient approximate nearest neighbor search

## Troubleshooting & Known Issues

### 1. **Database Connection Issues**
   - **Problem**: Connection fails with "localhost"
   - **Solution**: Use `127.0.0.1` instead of `localhost` in your configuration

### 2. **Environment Variables Not Loading**
   - **Problem**: `.env` file not being read
   - **Solution**: Ensure the `.env` file is in the `app/` directory, not the project root

### 3. **Vector Dimension Mismatch**
   - **Problem**: "vector dimension mismatch" error
   - **Solution**: The bge-m3 model uses 1024 dimensions, not 1536. Update your configuration accordingly

### 4. **Predicates Bug in timescale_vector**
   - **Problem**: `TypeError: Subscripted generics cannot be used with class and instance checks`
   - **Solution**: This is a bug in `timescale_vector` v0.0.7 with Python 3.9. Use `metadata_filter` instead of `Predicates` for filtering. The demo code in `similarity_search.py` has been commented out.

### 5. **Infini-AI API Configuration**
   - **Problem**: API calls failing
   - **Solution**: Ensure your API key is correct and the base URL is set to `https://cloud.infini-ai.com/maas/v1`

## Using ANN Search Indexes

Timescale Vector offers indexing options to accelerate similarity queries, particularly beneficial for large vector datasets (10k+ vectors):

1. **Supported indexes**:
   - `timescale_vector_index` (default): A DiskANN-inspired graph index
   - `pgvector's HNSW`: Hierarchical Navigable Small World graph index
   - `pgvector's IVFFLAT`: Inverted file index

2. The DiskANN-inspired index is Timescale's latest offering, providing improved performance. Refer to the [Timescale Vector explainer blog](https://www.timescale.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost/) for detailed information and benchmarks.

For optimal query performance, creating an index on the embedding column is recommended, especially for large vector datasets.

## Cosine Similarity in Vector Search

### What is Cosine Similarity?

Cosine similarity measures the cosine of the angle between two vectors in a multi-dimensional space. It's a measure of orientation rather than magnitude.

- **Range**: -1 to 1 (for normalized vectors, which is typical in text embeddings)
- **1**: Vectors point in the same direction (most similar)
- **0**: Vectors are orthogonal (unrelated)
- **-1**: Vectors point in opposite directions (most dissimilar)

### Cosine Distance

In pgvector, the `<=>` operator computes cosine distance, which is 1 - cosine similarity.

- **Range**: 0 to 2
- **0**: Identical vectors (most similar)
- **1**: Orthogonal vectors
- **2**: Opposite vectors (most dissimilar)

### Interpreting Results

When you get results from similarity_search:

- Lower distance values indicate higher similarity.
- A distance of 0 would mean exact match (rarely happens with embeddings).
- Distances closer to 0 indicate high similarity.
- Distances around 1 suggest little to no similarity.
- Distances approaching 2 indicate opposite meanings (rare in practice).

## Quick Local Testing

To quickly test the system locally:

1. **Start the database**:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

2. **Set up Python environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp app/example.env app/.env
   # Edit app/.env to add your Infini-AI API key
   ```

4. **Test database connection**:
   ```bash
   python app/database/connect_postgres.py
   ```

5. **Insert vectors**:
   ```bash
   python app/insert_vectors.py
   ```

6. **Run similarity search**:
   ```bash
   python app/similarity_search.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Timescale](https://www.timescale.com/) for pgvectorscale
- [Infini-AI](https://cloud.infini-ai.com) for the embedding and LLM models
- Original tutorial by [Dave Ebbelaar](https://github.com/daveebbelaar)
