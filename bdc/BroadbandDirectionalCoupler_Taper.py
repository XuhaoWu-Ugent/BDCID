from si_fab import all as pdk
from ipkiss3 import all as i3
from ipkiss3.pcell.trace.window.window import PathTraceWindow
from si_fab.components.waveguides.generic.trace import GenericWaveguideTemplate


class DoubleWavTemplate(GenericWaveguideTemplate):
    cladding_width = i3.PositiveNumberProperty(default=1.0)
    start_offsets = i3.ListProperty()
    end_offsets = i3.ListProperty()

    def _default_start_offsets(self):
        return [-0.55, 0.1]

    def _default_end_offsets(self):
        return [-0.1, 0.55]

    class Layout(GenericWaveguideTemplate.Layout):
        cladding_layer = i3.LayerProperty()

        def _default_core_layer(self):
            return i3.TECH.PPLAYER.SI

        def _default_cladding_layer(self):
            return i3.TECH.PPLAYER.NONE

        def _default_windows(self):
            windows = []

            for so, eo in zip(self.start_offsets, self.end_offsets):
                windows.append(PathTraceWindow(layer=self.core_layer,
                                               start_offset=so,
                                               end_offset=eo))

            windows.append(PathTraceWindow(layer=self.cladding_layer,
                                           start_offset=-self.cladding_width / 2.0,
                                           end_offset=self.cladding_width / 2.0))

            return windows


class DirectionalCouplerTaper(i3.PCell):
    trace_template = i3.TraceTemplateProperty(locked=True)

    def _default_trace_template(self):
        return pdk.SiWireWaveguideTemplate()

    port_trace_template_en = i3.TraceTemplateProperty(locked=True)

    def _default_port_trace_template_en(self):
        return DoubleWavTemplate()

    wg_length = i3.PositiveNumberProperty(default=1.0, doc="length of the entering/exiting waveguides")
    wg_width = i3.PositiveNumberProperty(default=0.45, doc="width of the entering/exiting waveguides")
    t_length = i3.PositiveNumberProperty(default=4.21, doc="length of the taper section")
    t_width_u = i3.PositiveNumberProperty(default=0.4365, doc="width of the upper taper")
    t_width_l = i3.PositiveNumberProperty(default=0.283, doc="width of the lower taper")
    coupler_spacing = i3.PositiveNumberProperty(default=0.2,
                                                doc="Separation of the waveguides in the whole structure sidewall-to-sidewall")
    cladding_offset = i3.PositiveNumberProperty(default=1.0,
                                                doc="Offset of the cladding layer with respect to the ports")

    port_trace_template_ex = i3.TraceTemplateProperty(locked=True)

    def _default_port_trace_template_ex(self):
        return DoubleWavTemplate(start_offsets=[-self.t_width_l - self.coupler_spacing / 2., self.coupler_spacing / 2.],
                                 end_offsets=[-self.coupler_spacing / 2., self.t_width_u + self.coupler_spacing / 2.])

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

            # taper (upper/lower)
            s_u1 = i3.Shape(points=[(0.0, self.coupler_spacing / 2.), (self.t_length, self.coupler_spacing / 2.)])
            s_u = i3.Shape([(self.t_length, self.t_width_u + self.coupler_spacing / 2.),
                            (0.0, self.wg_width + self.coupler_spacing / 2.)], start_face_angle=180.0,
                           end_face_angle=180.0)
            s_u2 = i3.ShapeFitClampedCubicSpline(original_shape=s_u, discretisation=.1)
            shape_u = s_u1 + s_u2
            shape_u.close()
            elems += i3.Boundary(shape=shape_u, layer=core_layer)

            s_l1 = i3.Shape(points=[(0.0, -self.coupler_spacing / 2.), (self.t_length, -self.coupler_spacing / 2.)])
            s_l = i3.Shape(
                [(self.t_length, -self.t_width_l - self.coupler_spacing / 2.),
                 (0.0, -self.wg_width - self.coupler_spacing / 2.)],
                start_face_angle=180.0, end_face_angle=180.0)
            s_l2 = i3.ShapeFitClampedCubicSpline(original_shape=s_l, discretisation=.1)
            shape_l = s_l1 + s_l2
            shape_l.close()
            elems += i3.Boundary(shape=shape_l, layer=core_layer)

            # exiting waveguides
            shape_exiting_1 = [(self.t_length, self.t_width_u / 2. + self.coupler_spacing / 2.),
                               (self.t_length + self.wg_length, self.t_width_u / 2. + self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_exiting_1, line_width=self.t_width_u)
            shape_exiting_2 = [(self.t_length, -self.t_width_l / 2. - self.coupler_spacing / 2.),
                               (self.t_length + self.wg_length, -self.t_width_l / 2. - self.coupler_spacing / 2.)]
            elems += i3.Path(layer=core_layer, shape=shape_exiting_2, line_width=self.t_width_l)

            # Cladding layer
            box_size = elems.size_info().size + i3.Coord2((2 * self.cladding_offset, 2 * self.cladding_offset))
            elems += i3.Rectangle(layer=cladding_layer, center=(self.t_length / 2., 0.0), box_size=box_size)
            return elems

        #        def _generate_ports(self, ports):
        #            x1 = -self.wg_length
        #            y11 = self.wg_width / 2. + self.coupler_spacing / 2.
        #            y12 = -self.wg_width / 2. - self.coupler_spacing / 2.
        #            ports += i3.OpticalPort(name="in1", position=(x1, y11), angle=180.0, trace_template=self.trace_template)
        #            ports += i3.OpticalPort(name="in2", position=(x1, y12), angle=180.0, trace_template=self.trace_template)
        #            x2 = self.t_length + self.wg_length
        #            y21 = self.t_width_u / 2. + self.coupler_spacing / 2.
        #            y22 = -self.t_width_l / 2. - self.coupler_spacing / 2.
        #            ports += i3.OpticalPort(name="out1", position=(x2, y21), angle=0.0, trace_template=self.trace_template)
        #            ports += i3.OpticalPort(name="out2", position=(x2, y22), angle=0.0, trace_template=self.trace_template)
        #            return ports

        def _generate_ports(self, ports):
            x1 = -self.wg_length
            y1 = 0.0
            ports += i3.OpticalPort(name="in1", position=(x1, y1), angle=180.0,
                                    trace_template=self.port_trace_template_en)
            x2 = self.t_length + self.wg_length
            y2 = 0.0
            ports += i3.OpticalPort(name="out1", position=(x2, y2), angle=0.0,
                                    trace_template=self.port_trace_template_ex)
            # ports += i3.OpticalPort(name="out1", position=(x2, y2), angle=0.0, trace_template=self.port_trace_template_ex(start_offsets=[-self.t_width_l - self.coupler_spacing / 2., -self.coupler_spacing / 2.], end_offsets=[self.coupler_spacing / 2., self.wg_width + self.coupler_spacing / 2.]))
            return ports

    class Netlist(i3.NetlistFromLayout):
        pass

# cell = DirectionalCouplerTaper()
# lv = cell.Layout()
# lv.visualize(annotate=True)
# lv.write_gdsii("dc.gds")

# print DirectionalCouplerTaper().Netlist().terms
