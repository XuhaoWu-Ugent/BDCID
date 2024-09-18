from si_fab import all as pdk
from ipkiss3 import all as i3
from BroadbandDirectionalCoupler_Taper import DoubleWavTemplate


class DirectionalCoupler(i3.PCell):

    trace_template = i3.TraceTemplateProperty(locked=True)

    def _default_trace_template(self):
        return pdk.SiWireWaveguideTemplate()

    port_trace_template = i3.TraceTemplateProperty(locked=True)

    def _default_port_trace_template(self):
        return DoubleWavTemplate()

    wg_length = i3.PositiveNumberProperty(default=5., doc="length of the entering/exiting waveguides")
    wg_width = i3.PositiveNumberProperty(default=0.45, doc="width of the entering/exiting waveguides")
    t_length = i3.PositiveNumberProperty(default=16.244, doc="length of the taper section")
    t_width_u = i3.PositiveNumberProperty(default=0.533, doc="width of the upper taper")
    t_width_l = i3.PositiveNumberProperty(default=0.461, doc="width of the lower taper")
    coupler_spacing = i3.PositiveNumberProperty(default=0.2, doc="Separation of the waveguides in the whole structure "
                                                    "sidewall-to-sidewall")
    cladding_offset = i3.PositiveNumberProperty(default=1.0,
                                                doc="Offset of the cladding layer with respect to the ports")

    class Layout(i3.LayoutView):

        def _default_wg_width(self):
            return 0.45

        def _default_coupler_spacing(self):
            return 0.2

        def _generate_elements(self, elems):
            core_layer = self.trace_template.core_layer
            cladding_layer = self.trace_template.cladding_layer

            # entrance waveguides
            shape_entrance_1 = [(-self.wg_length, self.wg_width / 2. + self.coupler_spacing / 2.),
                                (0.0, self.wg_width / 2. + self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_entrance_1, line_width=self.wg_width)
            shape_entrance_2 = [(-self.wg_length, -self.wg_width / 2. - self.coupler_spacing / 2.),
                                (0.0, -self.wg_width / 2. - self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_entrance_2, line_width=self.wg_width)

            # taper (upper/lower) fixing the number of control points to 5
            s_u1 = i3.Shape(points=[(0.0, self.coupler_spacing / 2.), (self.t_length, self.coupler_spacing / 2.)])
            s_u = i3.Shape([(self.t_length, self.wg_width + self.coupler_spacing / 2.),
                            (self.t_length / 5 * 3, self.t_width_u + self.coupler_spacing / 2.),
                            (self.t_length / 2 * 1, self.t_width_u + self.coupler_spacing / 2.),
                            (self.t_length / 5 * 2, self.t_width_u + self.coupler_spacing / 2.),
                            (0.0, self.wg_width + self.coupler_spacing / 2.)], start_face_angle=180.0,
                           end_face_angle=180.0)
            s_u2 = i3.ShapeFitClampedCubicSpline(original_shape=s_u, discretisation=.1)
            shape_u = s_u1 + s_u2
            shape_u.close()
            elems += i3.Boundary(shape=shape_u, layer=core_layer)

            s_l1 = i3.Shape(points=[(0.0, -self.coupler_spacing / 2.), (self.t_length, -self.coupler_spacing / 2.)])
            s_l = i3.Shape(
                [(self.t_length, -self.wg_width - self.coupler_spacing / 2.),
                 (self.t_length / 5 * 3, -self.t_width_l - self.coupler_spacing / 2.),
                 (self.t_length / 2 * 1, -self.t_width_l - self.coupler_spacing / 2.),
                 (self.t_length / 5 * 2, -self.t_width_l - self.coupler_spacing / 2.),
                 (0.0, -self.wg_width - self.coupler_spacing / 2.)],
                start_face_angle=180.0, end_face_angle=180.0)
            s_l2 = i3.ShapeFitClampedCubicSpline(original_shape=s_l, discretisation=.1)
            shape_l = s_l1 + s_l2
            shape_l.close()
            elems += i3.Boundary(layer=core_layer, shape=shape_l)

            # exiting waveguides
            shape_exiting_1 = [(self.t_length, self.wg_width / 2. + self.coupler_spacing / 2.),
                               (self.t_length + self.wg_length, self.wg_width / 2. + self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_exiting_1, line_width=self.wg_width)
            shape_exiting_2 = [(self.t_length, -self.wg_width / 2. - self.coupler_spacing / 2.),
                               (self.t_length + self.wg_length, -self.wg_width / 2. - self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_exiting_2, line_width=self.wg_width)

            # Cladding layer
            box_size = elems.size_info().size + i3.Coord2((2 * self.cladding_offset, 2 * self.cladding_offset))
            elems += i3.Rectangle(layer=cladding_layer, center=(self.t_length / 2., 0.0), box_size=box_size)
            return elems

        def _generate_ports(self, ports):
            x1 = -self.wg_length
            y1 = 0.0
            ports += i3.OpticalPort(name="in1", position=(x1, y1), angle=180.0, trace_template=self.port_trace_template)
            x2 = self.t_length + self.wg_length
            y2 = 0.0
            ports += i3.OpticalPort(name="out1", position=(x2, y2), angle=0.0,
                                    trace_template=self.port_trace_template)
            return ports

    class Netlist(i3.NetlistFromLayout):
        pass


if __name__ == '__main__':
    cell = DirectionalCoupler()
    lv = cell.Layout()
    lv.visualize(annotate=True)
    print(lv.ports)
    lv.visualize_2d(show=False)
    cs = lv.cross_section(cross_section_path=i3.Shape([(1.5, -1), (1.5, 1)]))
    cs.visualize()
