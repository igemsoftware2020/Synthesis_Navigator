# How To Deploy

Our software can be deployed on your own Linux server for a better performance. We have tested the deployment steps on CentOS 7.7.

### STEP I

Update your system and install docker.

```
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```

### STEP II

Clone our repo and download extra data.

Put the downloaded files into the following directories.

```
mv ~/Download/db.sqlite3 Synthesis_Navigator-master/
mv ~/Download/Compound.csv Synthesis_Navigator-master/statics/data_download/
mv ~/Download/Enzyme.csv Synthesis_Navigator-master/statics/data_download/
mv ~/Download/Reaction.csv Synthesis_Navigator-master/statics/data_download/
mv ~/Download/SyntheticBay.db Synthesis_Navigator-master/statics/data_download/
```

### STEP III

Build docker image.

```
cd Synthesis_Navigator-master/
docker build -t TongjiSoftware/Synthesis_Navigator:1.0 .
```

### STEP IV

Run the container.

```
docker run -it --rm -p 8000:8000 TongjiSoftware/Synthesis_Navigator:1.0 
```

### STEP V

Open 127.0.0.1/Home in your browser (Chrome is recommended).Enjoy:)

You can modify settings.py to suit your environment.
