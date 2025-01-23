-- DATABASESCHEMA 

DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS data;


CREATE TABLE berlin_osm_pois (
    id SERIAL PRIMARY KEY,
    fclass VARCHAR(255),    -- Type of POI (e.g., kindergarten, school, college)
    geom GEOMETRY(POINT, 4326)  -- Point geometry column, EPSG 4326 (WGS 84)
);

CREATE TABLE hamburg_osm_pois (
    id SERIAL PRIMARY KEY,
    fclass VARCHAR(255),    -- Type of POI (e.g., kindergarten, school, college)
    geom GEOMETRY(POINT, 4326)  -- Point geometry column, EPSG 4326 (WGS 84)
);

CREATE TABLE berlin_districts (
    id SERIAL PRIMARY KEY,
    district_name VARCHAR(255),
    geom GEOMETRY(POLYGON, 4326)  -- Polygon geometry for each district
);


CREATE TABLE hamburg_districts (
    id SERIAL PRIMARY KEY,
    district_name VARCHAR(255),
    geom GEOMETRY(POLYGON, 4326)  -- Polygon geometry for each district
);

CREATE TABLE berlin_districts_data (
    district_name VARCHAR(255) PRIMARY KEY,
    population INT,
    population_age_under_18_count INT,
    population_age_under_18_percentage DECIMAL(5, 2),
    population_age_65_count INT,
    population_age_65_percentage DECIMAL(5, 2),
    unemployment_percentage DECIMAL(5, 2),
    youth_unemployment_percentage DECIMAL(5, 2),
    communities_of_need_percentage DECIMAL(5, 2),
    communities_of_need_under_15_percentage DECIMAL(5, 2),
    grundsicherung_65_percentage DECIMAL(5, 2),
    population_migration_background_count INT,
    population_migration_background_percentage DECIMAL(5, 2)
);

CREATE TABLE hamburg_districts_data (
    district_name VARCHAR(255) PRIMARY KEY,
    population INT,
    population_age_under_18_count INT,
    population_age_under_18_percentage DECIMAL(5, 2),
    population_age_65_count INT,
    population_age_65_percentage DECIMAL(5, 2),
    unemployment_percentage DECIMAL(5, 2),
    youth_unemployment_percentage DECIMAL(5, 2),
    communities_of_need_percentage DECIMAL(5, 2),
    communities_of_need_under_15_percentage DECIMAL(5, 2),
    grundsicherung_65_percentage DECIMAL(5, 2),
    population_migration_background_count INT,
    population_migration_background_percentage DECIMAL(5, 2)
);
