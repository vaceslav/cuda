
# Install

## docker

- install docker
- install docker-compose
- instal NVIDIA driver and runtime  https://www.celantur.com/blog/run-cuda-in-docker-on-linux/
- define nvidia runtime /etc/docker/daemon.json 

        {
            "default-runtime": "nvidia",
            "runtimes": {
                "nvidia": {
                    "path": "/usr/bin/nvidia-container-runtime",
                    "runtimeArgs": []
                }
            }
        }

restart docker

    sudo systemctl stop docker
    sudo systemctl start docker

## python 

- install miniconda https://docs.conda.io/en/latest/miniconda.html#linux-installers

create new eviropment 

    conda create --name slava
    conda activate slava
    conda install -c rapidsai -c nvidia -c conda-forge -c defaults cudf=0.14 cuml=0.14 python=3.7 cudatoolkit=11.0 pymapd pygeohash
    #better cuda 11 and latest rapids
    conda install -c rapidsai -c nvidia -c conda-forge  -c defaults rapids=0.17 python=3.8 cudatoolkit=11.0 pymapd pygeohash
    conda install -c conda-forge hdbscan
    conda install -c conda-forge geojson







## login in omnisci db cli

    docker-compose exec db bash
    docker-compose exec db /omnisci/bin/omnisql -p HyperInteractive
    ./insert_sample_data
    /omnisci/bin/omnisql 

create table *portfolios*

    CREATE TABLE IF NOT EXISTS portfolios (
            id BIGINT NOT NULL, 
            lat FLOAT, lon FLOAT,
            geohash_1 TEXT ENCODING DICT,
            geohash_2 TEXT ENCODING DICT,
            geohash_3 TEXT ENCODING DICT,
            geohash_4 TEXT ENCODING DICT,
            geohash_5 TEXT ENCODING DICT,
            geohash_6 TEXT ENCODING DICT,
            geohash_7 TEXT ENCODING DICT,
            geohash_8 TEXT ENCODING DICT,
            tsi FLOAT,
            building TEXT ENCODING DICT
            );

    CREATE TABLE IF NOT EXISTS portfolios2 (
            portfolio TEXT ENCODING DICT,
            ID BIGINT NOT NULL,
            CountryCode TEXT ENCODING DICT,
            Latitude DOUBLE,
            Longitude DOUBLE,
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
            geohash_8 TEXT ENCODING DICT
    );

    CREATE TABLE IF NOT EXISTS model2layers (
            ID BIGINT NOT NULL,
            LayerName TEXT ENCODING DICT,
            ParentLayerId FLOAT
    );

     CREATE TABLE IF NOT EXISTS model2locations (
            ID BIGINT NOT NULL,
            LayerId BIGINT NOT NULL,
            CountryCode TEXT ENCODING DICT,
            Latitude DOUBLE,
            Longitude DOUBLE,
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
            geohash_8 TEXT ENCODING DICT
    );




#password: **HyperInteractive**

size of omnisci storage dir

    du -sh omnisci-storage


## FAQ

"NO NVIDIA GPU detected"

    rm -rf  ~/.nv/
    reboot


## sample apps

download city data from http://www.geonames.org

     wget https://download.geonames.org/export/dump/allCountries.zip -P data


https://gist.github.com/nathzi1505/d2aab27ff93a3a9d82dada1336c45041


https://www.server-world.info/en/note?os=Ubuntu_20.04&p=nvidia&f=1


password: HyperInteractive

docker run --runtime=nvidia  -d --runtime=nvidia   -p 6273-6280:6273-6280   omnisci/core-os-cuda

docker exec -it 9e01e520c30c bash



conda install -c conda-forge pymapd

conda create -n rapids-0.17 -c rapidsai -c nvidia -c conda-forge -c defaults rapids-blazing=0.17 python=3.8 cudatoolkit=10.1



pip install pymapd


https://rapids.ai/start.html


conda install -c rapidsai -c nvidia -c conda-forge -c defaults rapids-blazing=0.17 python=3.8 cudatoolkit=10.1




#
# To activate this environment, use
#
#     $ conda activate rapids-core-0.17
#
# To deactivate an active environment, use
#
#     $ conda deactivate



conda create --name slava
conda activate slava
conda install -c conda-forge -c nvidia/label/cuda10.0 -c rapidsai/label/cuda10.0 -c numba -c defaults cudf pymapd python=3.7

conda create -n omnisci-gpu -c rapidsai -c nvidia -c conda-forge -c defaults cudf=0.15 python=3.7 cudatoolkit=10.2 pymapd

// working
conda install -c rapidsai -c nvidia -c conda-forge -c defaults cudf=0.14 python=3.7 cudatoolkit=10.2 pymapd


watch -n 1 nvidia-smi


add columns

    ALTER TABLE nyc_trees_2015_683k ADD COLUMN geohash_1 TEXT ENCODING DICT;
    



    row_number() over(partition by tree_id order by cretaed_at desc)



    select id,   row_number() over(partition by geohash_1  order by created_at desc)    from nyc_trees_2015_683k limit 100;





    CREATE TABLE IF NOT EXISTS portfolios id BIGINT NOT NULL, lat FLOAT, lon FLOAT);



    https://arxiv.org/pdf/2005.11177.pdf


https://towardsdatascience.com/geographic-clustering-with-hdbscan-ef8cb0ed6051
https://hdbscan.readthedocs.io/en/latest/index.html
https://hdbscan.readthedocs.io/en/latest/how_to_use_epsilon.html





select count(*) from portfolios where  lon >= -141.06445312500003 AND lat >= 6.839169626342808 AND lon <= 172.529296875 AND lat <= 81.54415925941507



# count for geohash group
select count(*)  from ( select count(*)  from portfolios where  lon >= -141.06445312500003 AND lat >= 6.839169626342808 AND lon <= 172.529296875 AND lat <= 81.54415925941507 group by geohash_4)


select  \n                        lat, \n                        lon \n                    from portfolios \n                    where \n                        lon >= -82.32673645019533 AND\n                        lat >= 28.072586166612016 AND\n                        lon <= -81.10176086425783 AND\n                        lat <= 28.59899156770566\n                  '