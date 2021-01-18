select 
    Sum_Insured,
    Losses, earthquake, 
    hail, 
    heat_wave,
    tornado, 
    Building_Type, 
    CountryCode

FROM portfolios 
where 
    PortfolioName = 'FAB_SampleLocations_100k_0' 
    AND (  
            ST_CONTAINS(ST_GeomFromText('POLYGON ((-124.453125 27.059126, -124.453125 52.802761, -66.972656 52.802761, -66.972656 27.059126, -124.453125 27.059126))', 4326), coor)  
            OR   
            ST_CONTAINS(ST_GeomFromText('POLYGON ((-8.261719 39.232253, 27.597656 56.36525, 37.265625 38.548165, 22.675781 44.840291, 22.675781 23.725012, -1.40625 27.215556, 10.019531 42.293564, -8.261719 39.232253))', 4326), coor) 
        );















SELECT 
        COUNT(*) 
FROM portfolios 
WHERE  
    Longitude >= -448.2421875 AND  
    Latitude >= -71.18775391813159 AND 
    Longitude <= 140.97656250000003 AND 
    Latitude <= 84.67351256610525 AND 
    PortfolioName = 'FAB_SampleLocations_1m_0' AND 
    ST_CONTAINS(ST_Point(Longitude, Latitude), 'POLYGON ((-129.023438 27.527758, -129.023438 60.844911, -65.390625 60.844911, -65.390625 27.527758, -129.023438 27.527758))')



    SELECT 
        COUNT(*) 
FROM portfolios 
WHERE  
    PortfolioName = 'FAB_SampleLocations_1m_0' AND 
    ST_CONTAINS(
        ST_GeomFromText('POLYGON ((-129.023438 27.527758, -129.023438 60.844911, -65.390625 60.844911, -65.390625 27.527758, -129.023438 27.527758))'),
        ST_Point(Longitude, Latitude)
    );



    select ST_SetSRID(ST_Point(Longitude, Latitude), 4326) from portfolios limit 5;















    ------------------------postgres


    SELECT COUNT(*) as pCount FROM portfolios 
    WHERE 
    longitude >= -245.91796875000003 AND  
    latitude >= -25.324166525738384 AND  
    longitude <= 48.69140625 AND 
    latitude <= 74.21198251594369 AND 
    portfolioname = 'FAB_SampleLocations_100k_0'