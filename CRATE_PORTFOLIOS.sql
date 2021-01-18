CREATE TABLE IF NOT EXISTS portfolios (
            PortfolioName TEXT ENCODING DICT,
            LayerId BIGINT NOT NULL,
            ID BIGINT NOT NULL,
            CountryCode TEXT ENCODING DICT,
            Latitude DOUBLE,
            Longitude DOUBLE,
            coor GEOMETRY(POINT, 4326),
            Income_Group INTEGER, 
            TSI_Group TEXT ENCODING DICT,
            Sum_Insured DOUBLE,
            Has_Losses BOOLEAN,
            Losses DOUBLE,
            Building_Type TEXT ENCODING DICT, 
            Sample_Rating TEXT ENCODING DICT,
            geohash_1 TEXT ENCODING DICT,
            geohash_2 TEXT ENCODING DICT,
            geohash_3 TEXT ENCODING DICT,
            geohash_4 TEXT ENCODING DICT,
            geohash_5 TEXT ENCODING DICT,
            geohash_6 TEXT ENCODING DICT,
            geohash_7 TEXT ENCODING DICT,
            geohash_8 TEXT ENCODING DICT,

            earthquake  SMALLINT,
            hail  SMALLINT,
            heat_wave  SMALLINT,
            tornado  SMALLINT
    );