-- =========================================
-- DF Engine Website DB Schema (MariaDB)
-- Docs-first, Benchmarks as flexible HTML
-- =========================================

-- Optional: create and select database
-- CREATE DATABASE df_engine_site CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE df_engine_site;

-- -----------------------------------------
-- DATASET
-- Canonical datasets used across docs/benchmarks
-- -----------------------------------------
CREATE TABLE dataset (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(128) NOT NULL,
    version       VARCHAR(32)  NOT NULL,
    description   TEXT,                 -- HTML allowed
    download_url  VARCHAR(512),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_dataset_name_version (name, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------
-- FUNCTION FAMILY
-- Semantic purpose/category (group_by, pivot, scan...)
-- Powers cards + navigation
-- -----------------------------------------
CREATE TABLE function_family (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    slug          VARCHAR(64)  NOT NULL,
    display_name  VARCHAR(128) NOT NULL,
    description   TEXT,                 -- HTML allowed
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_family_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------
-- FUNCTION IMPLEMENTATION
-- Concrete function / strategy (same semantic family can have many impls)
-- api_level says "high" or "low"
-- default_dataset_id is the dataset you want shown by default on the doc page
-- -----------------------------------------
CREATE TABLE function_impl (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    family_id           INT NOT NULL,

    real_name           VARCHAR(128) NOT NULL,
    api_level           ENUM('high', 'low') NOT NULL,

    signature_html      TEXT,   -- stored as HTML (or code preformatted as HTML)
    description_html    TEXT,   -- stored as HTML

    default_dataset_id  INT NULL,

    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    KEY idx_family (family_id),
    KEY idx_api_level (api_level),
    KEY idx_default_dataset (default_dataset_id),

    CONSTRAINT fk_impl_family
        FOREIGN KEY (family_id)
        REFERENCES function_family(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_impl_default_dataset
        FOREIGN KEY (default_dataset_id)
        REFERENCES dataset(id)
        ON DELETE SET NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------
-- BENCHMARK
-- Flexible, HTML-first benchmark blocks.
-- One function_impl can have multiple benchmarks (different workloads / variants).
-- dataset_id lets you keep everything aligned to the canonical dataset,
-- but allows alternative datasets when needed.
-- -----------------------------------------
CREATE TABLE benchmark (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    function_impl_id  INT NOT NULL,

    title             VARCHAR(256) NOT NULL,
    description_html  LONGTEXT NOT NULL,

    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    KEY idx_bench_impl (function_impl_id),

    UNIQUE KEY uq_benchmark_function (function_impl_id);

    CONSTRAINT fk_bench_impl
        FOREIGN KEY (function_impl_id)
        REFERENCES function_impl(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE benchmark_dataset (
    benchmark_id  INT NOT NULL,
    dataset_id    INT NOT NULL,

    PRIMARY KEY (benchmark_id, dataset_id),

    CONSTRAINT fk_bd_benchmark
        FOREIGN KEY (benchmark_id)
        REFERENCES benchmark(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_bd_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES dataset(id)
        ON DELETE RESTRICT

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------
-- GET STARTED
-- Minimal curated entry points into the docs
-- -----------------------------------------
CREATE TABLE get_started (
    id                INT AUTO_INCREMENT PRIMARY KEY,

    function_impl_id  INT NOT NULL,
    goal              VARCHAR(256) NOT NULL,  -- "Fast grouping on large datasets"

    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_get_started_function (function_impl_id),

    CONSTRAINT fk_get_started_function
        FOREIGN KEY (function_impl_id)
        REFERENCES function_impl(id)
        ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- END
-- =========================================



