from typing import List

import random
from pathlib import Path

import faker
import random
import datetime
import ics
from sqlmodel import Field, SQLModel, create_engine, Session, select
import sqlalchemy
from loguru import logger
import numpy

from tuttle.model import (
    Address,
    Contact,
    Client,
    Project,
    Contract,
    TimeUnit,
    Cycle,
    User,
    BankAccount,
    Invoice,
    InvoiceItem,
)


def create_fake_contact(
    fake: faker.Faker,
):
    try:
        street_line, city_line = fake.address().splitlines()
        a = Address(
            id=id,
            street=street_line.split(" ")[0],
            number=street_line.split(" ")[1],
            city=city_line.split(" ")[1],
            postal_code=city_line.split(" ")[0],
            country=fake.country(),
        )
        first_name, last_name = fake.name().split(" ", 1)
        contact = Contact(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=fake.email(),
            company=fake.company(),
            address_id=a.id,
            address=a,
        )
        return contact
    except Exception as ex:
        logger.error(ex)
        logger.error(f"Failed to create fake contact, trying again")
        return create_fake_contact(fake)


def create_fake_client(
    invoicing_contact: Contact,
    fake: faker.Faker,
):
    client = Client(
        id=id,
        name=fake.company(),
        invoicing_contact=invoicing_contact,
    )
    return client


def create_fake_contract(
    client: Client,
    fake: faker.Faker,
) -> Contract:
    """
    Create a fake contract for the given client.
    """
    return Contract(
        title=f"{client.name} service contract",
        client=client,
        signature_date=fake.date_this_year(before_today=True),
        start_date=fake.date_this_year(after_today=True),
        rate=fake.random_int(1, 1000),
        currency="EUR",  # TODO: Use actual currency
        VAT_rate=random.random() * 0.19,
        unit=random.choice(list(TimeUnit)),
        units_per_workday=random.randint(1, 12),
        volume=fake.random_int(1, 1000),
        term_of_payment=fake.random_int(1, 31),
        billing_cycle=random.choice([Cycle.weekly, Cycle.monthly, Cycle.quarterly]),
    )


def create_fake_project(
    contract: Contract,
    fake: faker.Faker,
):
    project_title = fake.bs()
    project = Project(
        title=project_title,
        tag="-".join(project_title.split(" ")[:2]).lower(),
        description=fake.paragraph(nb_sentences=2),
        unique_tag=project_title.split(" ")[0].lower(),
        is_completed=fake.pybool(),
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=80),
        contract=contract,
    )
    return project


def invoice_number_counting():
    count = 0
    while True:
        count += 1
        yield count


invoice_number_counter = invoice_number_counting()


def create_fake_invoice(project: Project, fake: faker.Faker) -> Invoice:
    """
    Create a fake invoice object with random values.

    Args:
    project (Project): The project associated with the invoice.
    fake (faker.Faker): An instance of the Faker class to generate random values.

    Returns:
    Invoice: A fake invoice object.
    """
    invoice_number = next(invoice_number_counter)
    invoice = Invoice(
        number=invoice_number,
        date=datetime.date.today(),
        sent=fake.pybool(),
        paid=fake.pybool(),
        cancelled=fake.pybool(),
        contract=project.contract,
        project=project,
        rendered=fake.pybool(),
    )
    number_of_items = fake.random_int(min=1, max=5)
    for _ in range(number_of_items):
        unit = fake.random_element(elements=("hours", "days"))
        if unit == "hours":
            unit_price = abs(round(numpy.random.normal(50, 20), 2))
        elif unit == "days":
            unit_price = abs(round(numpy.random.normal(500, 200), 2))
        vat_rate = round(numpy.random.uniform(0.05, 0.25), 2)
        invoice_item = InvoiceItem(
            start_date=fake.date_this_decade(),
            end_date=fake.date_this_decade(),
            quantity=fake.random_int(min=1, max=10),
            unit=unit,
            unit_price=unit_price,
            description=fake.sentence(),
            VAT_rate=vat_rate,
            invoice=invoice,
        )
        assert invoice_item.invoice == invoice
    return invoice


def create_fake_data(
    n: int = 10,
):
    locales = [
        "de_DE",
        "de_CH",
        "de_AT",
        "en_US",
        "en_GB",
        "es_ES",
        "fr_FR",
        "it_IT",
        "sv_SE",
        "cz_CZ",
        "nl_NL",
        "pt_BR",
        "tr_TR",
    ]
    fake = faker.Faker(locale=locales)

    contacts = [create_fake_contact(fake) for _ in range(n)]
    clients = [create_fake_client(contact, fake) for contact in contacts]
    contracts = [create_fake_contract(client, fake) for client in clients]
    projects = [create_fake_project(contract, fake) for contract in contracts]

    invoices = [create_fake_invoice(project, fake) for project in projects]

    return projects, invoices


def create_demo_user() -> User:
    user = User(
        name="Harry Tuttle",
        subtitle="Heating Engineer",
        website="https://tuttle-dev.github.io/tuttle/",
        email="mail@tuttle.com",
        phone_number="+55555555555",
        VAT_number="27B-6",
        address=Address(
            name="Harry Tuttle",
            street="Main Street",
            number="450",
            city="Somewhere",
            postal_code="555555",
            country="Brazil",
        ),
        bank_account=BankAccount(
            name="Giro",
            IBAN="BZ99830994950003161565",
            BIC="BANKINFO101",
        ),
    )
    return user


def create_fake_calendar(project_list: List[Project]) -> ics.Calendar:
    # create a new calendar
    calendar = ics.Calendar()

    # populate the calendar with events
    for project in project_list:
        # create a new event
        event = ics.Event()
        event.name = f"Meeting for {project.tag}"
        # randomly set the event duration between 1 and 8 hours
        event.duration = random.randint(1, 8), "hours"
        calendar.events.append(event)


def install_demo_data(
    n: int,
    db_path: str,
):
    db_path = f"""sqlite:///{db_path}"""
    logger.info(f"Installing demo data in {db_path}...")
    logger.info(f"Creating {n} fake projects...")
    projects, invoices = create_fake_data(n)
    logger.info(f"Creating database engine at: {db_path}...")
    db_engine = create_engine(db_path)
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(db_engine)

    logger.info("Creating demo user...")
    with Session(db_engine) as session:
        user = create_demo_user()
        session.add(user)
        session.commit()

    # add fake invoices
    logger.info("Adding fake invoices...")
    with Session(db_engine) as session:
        for invoice in invoices:
            session.add(invoice)
            session.commit()

    logger.info("Adding demo data to database...")
    with Session(db_engine) as session:
        for project in projects:
            session.add(project)
            session.commit()
    logger.info("Demo data installed.")


if __name__ == "__main__":
    install_demo_data(n=10)
