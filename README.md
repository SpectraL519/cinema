# Cinema ticket sales application
University project for "Databases and information systems" - WIP

<br />

### Setup

* Install [anaconda](https://www.anaconda.com/)

* Clone this repository and go to the created directory:

```
cd <repo_dir>/cinema
```

<br />

* Create an anaconda environment and activate it:

```
conda env create --name cinema python=3.9.7 --file docs/requirements.yaml
conda activate cinema
```

<br />

* Create the database on MySQL or MariaDB server like shown [here](docs/cinema_db.md)

* Run the configuration script:

```
python gen_config.py
```

<br />
<br />

### Running the application

```
python cinema.py
```

<br />
<br />

### Database specifications

* Entities diagram -> click [here](docs/entities.png)

* SQL code -> click [here](docs/db_cinema.md)
