"""Reject broken connector sensor routes before publishing DT images."""
import copy
import struct
import unittest

from source_dt import thermal_binding_errors


def cell(value):
    return struct.pack('>I', value)


class ThermalBindings(unittest.TestCase):
    def setUp(self):
        self.provider = '/soc/spmi/adc'
        self.zone = '/soc/thermal-zones/conn_therm'
        self.channel = self.provider + '/connector@2747'
        self.rules = [dict(zone=self.zone, provider=self.provider, channel=0x2747)]
        self.nodes = {
            '/': {}, '/soc': {}, '/soc/spmi': {}, '/soc/thermal-zones': {},
            self.provider: {'phandle': cell(17), '#thermal-sensor-cells': cell(1),
                            'compatible': b'qcom,spmi-adc5-gen4\0'},
            self.zone: {'thermal-sensors': cell(17) + cell(0x2747)},
            self.channel: {'reg': cell(0x2747), 'qcom,adc-tm-type': cell(1)},
        }

    def test_valid_and_reallocated_handles(self):
        for handle in (17, 903, 0x10001):
            self.nodes[self.provider]['phandle'] = cell(handle)
            self.nodes[self.zone]['thermal-sensors'] = cell(handle) + cell(0x2747)
            self.assertEqual(thermal_binding_errors(self.nodes, self.rules), [])
        self.nodes[self.provider]['linux,phandle'] = self.nodes[self.provider].pop('phandle')
        self.nodes[self.channel]['qcom,adc-tm-type'] = cell(2)
        self.assertEqual(thermal_binding_errors(self.nodes, self.rules), [])

    def test_disabled_or_missing_ancestors(self):
        for path in self.nodes:
            with self.subTest(path=path):
                nodes = copy.deepcopy(self.nodes)
                nodes[path]['status'] = b'disabled\0'
                self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])
                del nodes[path]
                self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])

    def test_wrong_channel_provider_and_tm_mode(self):
        mutations = [
            (self.zone, 'thermal-sensors', cell(18) + cell(0x2747)),
            (self.zone, 'thermal-sensors', cell(17) + cell(0x747)),
            (self.zone, 'thermal-sensors', cell(17)),
            (self.provider, 'phandle', cell(0)),
            (self.provider, '#thermal-sensor-cells', cell(2)),
            (self.provider, 'compatible', b'qcom,spmi-adc5\0'),
            (self.channel, 'reg', cell(0x747)),
            (self.channel, 'qcom,adc-tm-type', cell(0)),
            (self.channel, 'qcom,adc-tm-type', cell(3)),
        ]
        for path, prop, value in mutations:
            with self.subTest(path=path, prop=prop, value=value):
                nodes = copy.deepcopy(self.nodes)
                nodes[path][prop] = value
                self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])
                del nodes[path][prop]
                self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])

    def test_ambiguous_channels_and_handles(self):
        nodes = copy.deepcopy(self.nodes)
        nodes[self.provider + '/duplicate'] = copy.deepcopy(nodes[self.channel])
        self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])
        nodes = copy.deepcopy(self.nodes)
        nodes['/soc/other'] = {'phandle': cell(17)}
        self.assertEqual(thermal_binding_errors(nodes, self.rules), [self.zone])


if __name__ == '__main__':
    unittest.main()
