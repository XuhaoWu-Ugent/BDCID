import si_fab.all as pdk
import ipkiss3.all as i3


class BroadbandDirectionalCoupler(i3.PCell):
    """Broadband directional coupler with a taper section."""
    data_tag = i3.LockedProperty()
    wg_length = i3.PositiveNumberProperty(default=1.0, doc="length of the entering/exiting waveguides")
    wg_width = i3.PositiveNumberProperty(default=0.38, doc="width of the entering/exiting waveguides")
    t_length = i3.PositiveNumberProperty(default=4.21, doc="length of the taper section")
    t_width_u = i3.ListProperty(doc="widths of the upper taper")
    t_width_l = i3.ListProperty(doc="widths of the lower taper")
    coupler_spacing = i3.PositiveNumberProperty(
        default=0.2,
        doc="Separation of the waveguides in the whole structure sidewall-to-sidewall"
    )
    cladding_offset = i3.PositiveNumberProperty(
        default=1.0,
        doc="Offset of the cladding layer with respect to the ports"
    )
    n_points = i3.IntProperty(default=11, doc="Number of control points for the taper")
    trace_template = i3.TraceTemplateProperty()

    def _default_data_tag(self):
        return "bdc_oband"

    def _default_name(self):
        return self.data_tag.upper()

    def _default_trace_template(self):
        tt = pdk.SiWireWaveguideTemplate()
        tt.Layout(
            core_width=self.wg_width,
            cladding_width=self.cladding_offset
        )
        return tt

    def _default_t_width_l(self):
        return [
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width,
            self.wg_width
        ]

    def _default_t_width_u(self):
        return [
            self.wg_width,
            self.wg_width,
            self.wg_width + 0.1,
            self.wg_width,
            self.wg_width,
            self.wg_width + 0.1,
            self.wg_width + 0.15,
            self.wg_width + 0.18,
            self.wg_width + 0.15,
            self.wg_width + 0.1,
            self.wg_width
        ]

    class Layout(i3.LayoutView):

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

            # taper (upper/lower) fixing the number of control points
            n_segments = self.n_points - 1
            s_l_list = []
            s_u_list = []
            for i in range(self.n_points):
                s_l_list.append(
                    (self.t_length / n_segments * (n_segments - i),
                     -self.t_width_l[i] - self.coupler_spacing / 2.)
                )
                s_u_list.append(
                    (self.t_length / n_segments * (n_segments - i),
                     self.t_width_u[i] + self.coupler_spacing / 2.)
                )
            s_u1 = i3.Shape(points=[(0.0, self.coupler_spacing / 2.), (self.t_length, self.coupler_spacing / 2.)])
            s_u = i3.Shape(
                points=s_u_list,
                start_face_angle=180.0,
                end_face_angle=180.0
            )
            s_u2 = i3.ShapeFitClampedCubicSpline(original_shape=s_u, discretisation=.1)
            shape_u = s_u1 + s_u2
            shape_u.close()
            elems += i3.Boundary(shape=shape_u, layer=core_layer)

            s_l1 = i3.Shape(points=[(0.0, -self.coupler_spacing / 2.), (self.t_length, -self.coupler_spacing / 2.)])
            s_l = i3.Shape(
                points=s_l_list,
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
            y1 = -self.wg_width / 2. - self.coupler_spacing / 2
            y2 = self.wg_width / 2. + self.coupler_spacing / 2
            ports += i3.OpticalPort(name="in1", position=(x1, y1), angle=180.0, trace_template=self.trace_template)
            ports += i3.OpticalPort(name="in2", position=(x1, y2), angle=180.0, trace_template=self.trace_template)
            x2 = self.t_length + self.wg_length
            ports += i3.OpticalPort(name="out1", position=(x2, y1), angle=0.0,
                                    trace_template=self.trace_template)
            ports += i3.OpticalPort(name="out2", position=(x2, y2), angle=0.0,
                                    trace_template=self.trace_template)
            return ports

    class Netlist(i3.NetlistFromLayout):
        pass


if __name__ == '__main__':
    cell = BroadbandDirectionalCoupler()
    lv = cell.Layout()
    lv.visualize(annotate=True)
    print(lv.ports)
    lv.visualize_2d(show=False)
    cs = lv.cross_section(cross_section_path=i3.Shape([(1.5, -1), (1.5, 1)]))
    cs.visualize()
