import asyncio
import traceback
from vigobus import Vigobus
from vigobus.datasources.base import BaseDatasource
from vigobus.datasources.ds_qrhtml import DatasourceQrHtml
from vigobus.datasources.ds_vigoapi import DatasourceVigoApi


async def amain():
    datasources_selections = {
        "1": DatasourceQrHtml,
        "2": DatasourceVigoApi
    }
    print("Choose a datasource:")
    for key, datasource in datasources_selections.items():
        print(f"  {key}: {datasource.__name__}")

    selection = input("Enter: ")
    if selection not in datasources_selections:
        selection = "1"
    datasource_class: BaseDatasource = datasources_selections[selection]()

    while True:
        stop_id = input("Enter Stop ID (or 'exit' to quit): ")
        if stop_id.lower() == "exit":
            break

        # noinspection broad-exception
        try:
            stop_id_int = int(stop_id)
            stop = await datasource_class.get_stop(stop_id_int)
            if stop:
                position = ""
                if stop.position:
                    position = f", Position: ({stop.position.lat}, {stop.position.lon})"
                print(f"Stop ID: {stop.id}, Name: {stop.name}{position}")
            else:
                print(f"No stop found with ID {stop_id_int}.")

            buses = await datasource_class.get_buses(stop_id_int, get_all_buses=True)
            if buses.buses:
                print(f"Buses for Stop ID {stop_id_int}:")
                for bus in buses.buses:
                    distance = f", {bus.distance_meters} meters"\
                        if bus.distance_meters is not None \
                        else ", unknown distance"
                    print(f"  Bus {bus.line} {bus.route}, {bus.time_minutes} minutes{distance}")
            else:
                print(f"No buses found for Stop ID {stop_id_int}.")

        except ValueError:
            print("Please enter a valid integer for Stop ID.")

        except (KeyboardInterrupt, InterruptedError):
            break

        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(amain())
