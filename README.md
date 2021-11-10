# NYU-DevOps-Inventory/inventory

[![Build Status](https://github.com/NYU-DevOps-Inventory/inventory/actions/workflows/workflow.yml/badge.svg)](https://github.com/NYU-DevOps-Inventory/inventory/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/NYU-DevOps-Inventory/inventory/branch/main/graph/badge.svg?token=KRF89G3MKC)](https://codecov.io/gh/NYU-DevOps-Inventory/inventory)

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
.
├── Procfile
├── README.md
├── Vagrantfile
├── config.py
├── coverage.xml
├── manifest.yml
├── requirements.txt
├── runtime.txt
├── service
│   ├── __init__.py             - package initializer
│   ├── constants.py            - constansts of the app
│   ├── error_handlers.py       - http error codes
│   ├── models.py               - module with main database models
│   ├── routes.py               - module with service routes
│   └── status.py               - http status codes
├── setup.cfg
├── tests
│   ├── __init__.py             - package initializer
│   ├── factories.py            - factory to fake inventory data
│   ├── test_error_handlers.py  - test suite for error_handlers.py
│   ├── test_models.py          - test suite for models.py
│   └── test_routes.py          - test suite for routes.py
└── unittests.xml
```

## Database Schema

### `Condition` Enum

- `NEW`
- `OPEN_BOX`
- `USED`

### `Inventory` Model

| Field           | Type    | Description              | Primary Key | Nullable |
| :-------------- | :------ | :----------------------- | :---------: | :------: |
| `product_id`    | Integer | Product's ID             |     Yes     |    No    |
| `condition`     | Enum    | Inventory's condition    |     Yes     |    No    |
| `quantity`      | Integer | Inventory's quantity     |     No      |    No    |
| `restock_level` | Integer | Product's restock level  |     No      |   Yes    |
| `available`     | Boolean | Inventory's availability |     No      |    No    |

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
# Type one of the following tow commands to run the app
$ honcho start
$ FLASK_APP=service:app flask run -h 0.0.0.0
```

Now open your browser, you are expected to see the following text when browsing http://localhost:3000

```json
{
  "name": "Inventory REST API Service",
  "paths": "http://localhost:3000/inventory",
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

Note the type of `product_id` is `integer` and the type of `condition` is `string`.

For simplicity, we omit the types in the following table.

| Method   | URL                                                      | Operation                                                            |
| :------- | :------------------------------------------------------- | :------------------------------------------------------------------- |
| `GET`    | `/inventory`                                             | Return a list of all the inventory                                   |
| `GET`    | `/inventory/:product_id/condition/:condition`            | Return the Inventory with the given `product_id` and `condition`     |
| `POST`   | `/inventory`                                             | Create a new Inventory record in the database                        |
| `PUT`    | `/inventory/:product_id/condition/:condition`            | Update the Inventory with the given `product_id` and `condition`     |
| `PUT`    | `/inventory/:product_id/condition/:condition/activate`   | Activate the Inventory with the given `product_id` and `condition`   |
| `PUT`    | `/inventory/:product_id/condition/:condition/deactivate` | Deactivate the Inventory with the given `product_id` and `condition` |
| `DELETE` | `/inventory/:product_id/condition/:condition`            | Delete the Inventory with the given `product_id` and `condition`     |

In `POST`, the request body should be:

```json
{
  "product_id": Integer!,
  "quantity": Integer!,
  "condition": String!, // will convert to Enum in code
  "restock_level": Integer?,
  "available": Boolean!,
}
```

In `PUT`, the allowed keys in request body are:

```json
{
  // Update the inventory's quantity
  "quantity": Integer,

  // Increase the inventory's quantity
  "added_amount": Integer,

  // Update the inventory's restock_level (its condition must be Condition.NEW)
  "restock_level": Integer,
}
```

## Deployment

We also deploy our app by IBM Cloud Foundry.

Link: https://nyu-devops-inventory.us-south.cf.appdomain.cloud
