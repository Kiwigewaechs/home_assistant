"""define the sensors which listen to single QCell inverter properties."""
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import QCellsInverterConnector
from .api_poller import ApiPoller
from .const import DOMAIN, battery_device, inverter_device, pv_device
from .conversions import (
    div10,
    div100,
    get_battery_mode,
    get_intervter_mode,
    to_signed,
    twoway_div10,
    twoway_div100,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    inverter_api: QCellsInverterConnector = hass.data[DOMAIN][entry.entry_id]
    coordinator = ApiPoller(hass, inverter_api, entry.data["interval"])

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    q_cells_factory = QCellsSensorConfigFactory(
        coordinator, entry.data["sn"], entry.data["SW version"]
    )

    """
    async_add_entities(
        q_cells_factory(
            idx, None, SensorDeviceClass.POWER, f"QCells Sensor idx: {idx}"
        ).get_sensor()  # coordinator, idx, entry.data["sn"]
        for idx, _ in enumerate(coordinator.data["Data"])
    )
    """

    sensor_list = []
    # QCells Inverter AC Power:

    sensor_list.append(
        q_cells_factory(
            0,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            "QCells Network Voltage Phase 1",
            div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            1,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            "QCells Network Voltage Phase 2",
            div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            2,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            "QCells Network Voltage Phase 3",
            div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            3,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            "QCells Output current Phase 1",
            twoway_div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            4,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            "QCells Output current Phase 2",
            twoway_div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            5,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            "QCells Output current Phase 3",
            twoway_div10,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            6,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Power Now Phase 1",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            7,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Power Now Phase 2",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            8,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Power Now Phase 3",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            9,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Inverter AC Power",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            14,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells PV1 Power",
            device_type=pv_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            15,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells PV2 Power",
            device_type=pv_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [14, 15],
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Total PV power",
            device_type=pv_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            16,
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            "QCells Grid Frequency Phase 1",
            div100,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            17,
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            "QCells Grid Frequency Phase 2",
            div100,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            18,
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            "QCells Grid Frequency Phase 3",
            div100,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            19,
            None,
            SensorDeviceClass.ENUM,
            "QCells Inverter Operation mode",
            get_intervter_mode,
            device_type=inverter_device,
            state_class=None,
        )
    )

    sensor_list.append(
        q_cells_factory(
            34,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Exported Power",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            39,
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            "QCells Battery Voltage",
            div100,
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            40,
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            "QCells Battery Current",
            twoway_div100,
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            41,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Battery Power",
            to_signed,
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            47,
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            "QCells Power Now",
            to_signed,
            device_type=inverter_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [68, 69],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total Energy",
            [div10, div10],
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [74, 75],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total Battery Discharge Energy",
            [div10, div10],
            device_type=battery_device,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [76, 77],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total Battery Charge Energy",
            [div10, div10],
            device_type=battery_device,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )
    )

    sensor_list.append(
        q_cells_factory(
            78,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Today's Battery Discharge Energy",
            div10,
            device_type=battery_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            79,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Today's Battery Charge Energy",
            div10,
            device_type=battery_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [80, 81],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total PV Energy",
            [div10, div10],
            device_type=pv_device,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )
    )

    sensor_list.append(
        q_cells_factory(
            82,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Today's Energy",
            div10,
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [86, 87],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total Feed-in Energy",
            [div100, div100],
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            [88, 89],
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Total Consumption",
            [div100, div100],
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )
    )

    sensor_list.append(
        q_cells_factory(
            90,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Today's Feed-in Energy",
            div100,
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            92,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            "QCells Today's Consumption",
            div100,
            device_type=inverter_device,
            state_class=SensorStateClass.TOTAL,
        )
    )

    sensor_list.append(
        q_cells_factory(
            103,
            PERCENTAGE,
            SensorDeviceClass.BATTERY,
            "QCells Inverter Battery Charging State",
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            105,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            "QCells Battery Temperature",
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            106,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY_STORAGE,
            "QCells Inverter Battery Remaining Energy",
            div10,
            device_type=battery_device,
        )
    )

    sensor_list.append(
        q_cells_factory(
            168,
            None,
            SensorDeviceClass.ENUM,
            "QCells Battery Mode",
            get_battery_mode,
            device_type=battery_device,
            state_class=None,
        )
    )

    async_add_entities(el.get_sensor() for el in sensor_list)


class QCellsSensorConfigFactory:
    """Use this class as a factory to generate QCell sensors. It knows about the generic properties of the complete integration devices."""

    def __init__(self, coordinator: ApiPoller, sn: str, sw_version: str) -> None:
        """Initialize the factory used to generate new QCells sensors.

        :param coordinator: The class used to poll new data
        :param sn: serial number
        :param sw_version: The software version of the QCells inverter.
        """
        self._coordinator = coordinator
        self._sn = sn
        self._sw_version = sw_version

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Create a specific QCell Sensor."""
        return QCellsSensorConfig(
            self._sn, self._sw_version, self._coordinator, *args, **kwds
        )


transform_fct = Callable[[float], float]
transform_complete = transform_fct | list[transform_fct]


class QCellsSensorConfig:
    """Define a sensor which measures properties of the QCell PV system."""

    def __init__(
        self,
        sn: str,
        sw_version: str,
        coordinator: ApiPoller,
        idx_api: int | list[int],
        measurement_unit: StrEnum,
        device_class: SensorDeviceClass,
        name: str = None,
        conversion: transform_complete | None = None,
        device_type: str | None = None,
        state_class: str = SensorStateClass.MEASUREMENT,
    ) -> None:
        """Initialize a configuration of a QCells Sensor.

        :param sn: The serial number of the inverter
        :param sw_version: The software version of the inverter
        :param coordinator: The coordinator class used to poll new data
        :param idx_api: The position of the sensor value in the QCell inverter's api
        :param measurement_unit: defines the physical si measurement unit of the incoming signal
        :param device class: Defines the device class and what it measures
        :param name: The name of the value which shall be sensed
        :param conversion: a callable which shall be applied to the measured values before saving them into the sensor.
        If it is none, then no conversion is applied.
        :param device_type: specifies if the sensor value belongs to the battery, the inverter or the photovoltaik elements themselves.
        :param state_class: is it a recent measurement value, a total value or a monotonically increasing value which is measured.
        """
        self._name = name
        self._idx_api = idx_api
        self._sn = sn
        self._sw_version = sw_version
        self._measurement_unit = measurement_unit
        self._device_class = device_class
        self._conversion: transform_complete | None = conversion
        self._coordinator = coordinator
        self._device_type = device_type
        self._state_class = state_class

    @property
    def name(self) -> str:
        """Return the device name."""
        if self._name is not None:
            return self._name
        else:
            return f"QCells Sensor {self.idx_api:03} for Inverter SN: {self.sn}"

    @property
    def idx_api(self):
        """Return the signal position in the API array which shall be measured."""
        return self._idx_api

    @property
    def sn(self):
        """Return the serial number."""
        return self._sn

    @property
    def sw_version(self) -> str:
        """Return the software version."""
        return self._sw_version

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return self._state_class

    @property
    def measurement_unit(self) -> StrEnum:
        """Return the measurement unit."""
        return self._measurement_unit

    @property
    def conversion(self) -> transform_complete:
        """Return the conversion functions. Must be callables."""
        if self._conversion is not None:
            return self._conversion
        elif isinstance(self.idx_api, int):
            return lambda x: x
        else:
            return [lambda x: x for el in self.idx_api]

    def __str__(self) -> str:
        """Return a name which expresses a unique identifier."""
        if isinstance(self.idx_api, int):
            idx_str = f"{self.idx_api:03}"
        else:
            idx_str = ""
            for el in self.idx_api:
                idx_str += f"{el:03}"
        return f"domain={DOMAIN}_sn={self.sn}_idx={idx_str}_name={self.name}"

    def get_sensor(self):
        """Construct a sensor from the given configuration."""
        return QCellsSensorReader(self, self._coordinator)

    @property
    def device_type(self):
        """Return the device to which the sensor shall belong."""
        return self._device_type


class QCellsSensorReader(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(
        self, sensor_config: QCellsSensorConfig, coordinator: ApiPoller
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=sensor_config.idx_api)
        self.idx = sensor_config.idx_api
        self._attr_unique_id = str(sensor_config)
        self._attr_name = sensor_config.name
        self._attr_device_class = sensor_config.device_class
        self._attr_native_unit_of_measurement = sensor_config.measurement_unit
        self.sensor_config = sensor_config
        self._attr_state_class = sensor_config.state_class

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        conversion = self.sensor_config.conversion

        if isinstance(self.idx, int):
            self._attr_native_value = conversion(
                self.coordinator.data["Data"][self.idx]
            )
        elif isinstance(self.idx, list) and isinstance(conversion, list):
            if len(self.idx) == len(conversion):
                self._attr_native_value = sum(
                    [
                        conversion[pos](self.coordinator.data["Data"][pos_el])
                        for pos, pos_el in enumerate(self.idx)
                    ]
                )
            else:
                raise LookupError(
                    "list lengths of idx to consume and conversion functions do not match"
                )
        else:
            raise NotImplementedError("this case is not yet implemented")
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo | None:
        """Define the device to which the sensor shall belong."""
        if self.sensor_config.device_type is not None:
            return DeviceInfo(
                identifiers={
                    (
                        DOMAIN,
                        self.sensor_config.sn,
                        self.sensor_config.device_type,
                    )
                },
                name=f"QCells {self.sensor_config.device_type}",
                manufacturer="QCells",
                sw_version=self.sensor_config.sw_version,
            )
        else:
            return None
