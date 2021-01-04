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