# NYU-DevOps-Inventory/inventory

## Get Started

This repository is a project of NYU course **CSCI-GA.2820: DevOps and Agile Methodologies** taught by John Rofrano, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, in **Fall 2021** semester.

This project is the back-end for an eCommerce website as a RESTful microservice for the inventory. This microservice supports the complete Create, Read, Update, & Delete (CRUD) lifecycle calls plus List, Query, Activate, and Deactivate.

## Team Members

|     Name      |     Email      |    Time Zone     |
| :-----------: | :------------: | :--------------: |
| Chen, Peng-Yu | pyc305@nyu.edu | New York (UTC-5) |
|  Lai, Yu-Wen  | yl8332@nyu.edu | New York (UTC-5) |
| Zhang, Haoran | hz2613@nyu.edu | New York (UTC-5) |
| Wen, Xuezhou  | xw2447@nyu.edu | New York (UTC-5) |
| Hung, Ginkel  | ch3854@nyu.edu | New York (UTC-5) |

## File Structure

```
├── service
│   ├── __init__.py        - package initializer
│   ├── error_handlers.py  - http error codes
│   ├── models.py          - module with main database models
│   ├── routes.py          - module with service routes
│   └── status.py          - http status codes
├── tests
│   ├── __init__.py        - package initializer
│   ├── factory_test.py    - factory to fake customer data
│   ├── test_models.py     - test suite for models.py
│   └── test_service.py    - test suite for routes.py
```

## Database Schema

### `Condition` Enum

- `NEW`
- `OPEN_BOX`
- `USED`

### `Inventory` Model

| Field           | Type    | Description             | Primary Key | Nullable |
| :-------------- | :------ | :---------------------- | :---------: | :------: |
| `product_id`    | Integer | Product's ID            |     Yes     |    No    |
| `condition`     | Enum    | Inventory's condition   |     Yes     |    No    |
| `quantity`      | Integer | Inventory's quantity    |     No      |    No    |
| `restock_level` | Integer | Product's restock level |     No      |   Yes    |

## Run the Service on Your Local PC

### Prerequisite Installations

Download [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).

### Run the Service in Terminal

Type below commands in your terminal:

```bash
$ git clone https://github.com/NYU-DevOps-Inventory/inventory.git
$ cd inventory
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ FLASK_APP=service:app flask run -h 0.0.0.0
```

Now open your browser, you are expected to see the following text when browsing http://0.0.0.0:5000

```json
{
  "name": "Inventory REST API Service",
  "paths": "http://0.0.0.0:5000/inventory",
  "version": "1.0"
}
```

### Run TDD Unit Tests

```bash
$ nosetests
```

If you want to see the lines of codes not tested, run:

```bash
$ coverage report -m
```

### Terminate the Service

Before you leave, be reminded to terminate the service by running

```bash
$ exit
$ vagrant halt
```

If the virtual machine is no longer needed, you can:

```bash
$ vagrant destroy
```

## APIs

For simplicity, note the type of `product_id` is `integer` and the type of `condition` is `string`.

| Method   | URL                                           | Operation                                                        |
| :------- | :-------------------------------------------- | :--------------------------------------------------------------- |
| `GET`    | `/inventory`                                  | Return a list of all the inventory                               |
| `GET`    | `/inventory/:product_id/condition/:condition` | Return the Inventory with the given `product_id` and `condition` |
| `POST`   | `/inventory`                                  | Create a new Inventory record in the database                    |
| `PUT`    | `/inventory/:product_id/condition/:condition` | Update the Inventory with the given `product_id` and `condition` |
| `DELETE` | `/inventory/:product_id/condition/:condition` | Delete the Inventory with the given `product_id` and `condition` |
