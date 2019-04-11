# -*- coding: utf-8 -*-
import wx
import math
import threading


def _remap(value, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min

    return (
        (((value - old_min) * new_range) / old_range) + new_min
    )


# noinspection PyPep8Naming
class VolumeCtrl(wx.Panel):

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=0.0,
        increment=1.0,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL | wx.BORDER_NONE,
        name=wx.PanelNameStr
    ):

        wx.Panel.__init__(
            self,
            parent,
            id=id,
            pos=pos,
            size=size,
            style=style,
            name=name
        )

        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.red_pen = wx.Pen(wx.Colour(200, 0, 0, 255), 2)
        self.green_pen = wx.Pen(wx.Colour(0, 200, 0, 255), 2)
        self.yellow_pen = wx.Pen(wx.Colour(200, 200, 0, 255), 2)
        self.black_pen = wx.Pen(wx.Colour(0, 0, 0, 150), 2)

        self.increment = increment

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._on_mouse_lost_capture)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.value = 0.0
        self._startup = value

    def SetValue(self, value):
        if 0.0 <= value <= 100.0:
            self.value = value
            self.Refresh()
            self.Update()

    def GetValue(self):
        return self.value

    def SetIncrement(self, increment):
        self.increment = increment

    def GetIncrement(self):
        return self.increment

    def _on_char_hook(self, evt):

        key_code = evt.GetKeyCode()

        if key_code in (wx.WXK_PAGEUP, wx.WXK_NUMPAD_PAGEUP):
            wx.CallAfter(self.SetValue, self.value + (self.increment * 10))

        elif key_code in (wx.WXK_PAGEDOWN, wx.WXK_NUMPAD_PAGEDOWN):
            wx.CallAfter(self.SetValue, self.value - (self.increment * 10))

        elif key_code in (
            wx.WXK_UP,
            wx.WXK_ADD,
            wx.WXK_NUMPAD_UP,
            wx.WXK_NUMPAD_ADD
        ):
            wx.CallAfter(self.SetValue, self.value + self.increment)

        elif key_code in (
            wx.WXK_DOWN,
            wx.WXK_SUBTRACT,
            wx.WXK_NUMPAD_DOWN,
            wx.WXK_NUMPAD_SUBTRACT
        ):
            wx.CallAfter(self.SetValue, self.value - self.increment)

        elif key_code in (wx.WXK_HOME, wx.WXK_NUMPAD_HOME):
            wx.CallAfter(self.SetValue, 0.0)

        elif key_code in (wx.WXK_END, wx.WXK_NUMPAD_END):
            wx.CallAfter(self.SetValue, 100.0)

        elif key_code - 48 in list(range(0, 10)):
            wx.CallAfter(self.SetValue, (key_code - 48) * 10.0)

        evt.Skip()

    def _on_erase_background(self, _):
        pass

    def _on_mouse_lost_capture(self, evt):
        self.ReleaseMouse()

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)
        evt.Skip()

    def _on_mouse_wheel(self, evt):

        wheel_delta = evt.GetWheelRotation()

        if wheel_delta < 0:
            wx.CallAfter(self.SetValue, self.value - self.increment)

        elif wheel_delta > 0:
            wx.CallAfter(self.SetValue, self.value + self.increment)

        evt.Skip()

    def _on_mouse_left_up(self, evt):

        if self.HasCapture():
            self.ReleaseMouse()

            def do():
                self.Refresh()
                self.Update()

            wx.CallAfter(do)

        evt.Skip()

    def _on_mouse_left_down(self, evt):
        client_rect = self.GetClientRect()
        boundary_rect = client_rect

        client_x, client_y, client_width, client_height = client_rect

        radius = (
            min(boundary_rect.GetWidth(), boundary_rect.GetHeight()) // 2
        ) * 0.85

        x_center = client_x + client_width // 2
        y_center = client_y + client_height // 2

        knob_radius = radius * 0.345 * 2
        knob_degree = _remap(self.value, 0.0, 100.0, 135.0, 405.0)
        knob_radian = math.radians(knob_degree)

        cos = math.cos(knob_radian)
        sin = math.sin(knob_radian)

        knob_x = x_center + int(round(knob_radius * cos))
        knob_y = y_center + int(round(knob_radius * sin))
        knob_radius = radius * 0.04 * 2

        start_x = knob_x - knob_radius
        start_y = knob_y - knob_radius
        end_x = knob_x + knob_radius
        end_y = knob_y + knob_radius

        x, y = evt.GetPosition()

        if start_x <= x <= end_x and start_y <= y <= end_y:
            self.CaptureMouse()

        evt.Skip()

    def _on_mouse_move(self, evt):

        if self.HasCapture():
            width, height = self.GetSize()
            center_x = width / 2
            center_y = height / 2

            x, y = evt.GetPosition()
            radians = math.atan2(y - center_y, x - center_x)

            degrees = math.degrees(radians)
            if degrees < 90:
                degrees += 360

            value = _remap(degrees, 135, 405, 0, 100)
            if value >= 100:
                value = 100.0

            elif value <= 0.0:
                value = 0.0

            elif value % self.increment:
                new_value = 0.0

                while value > new_value:
                    new_value += self.increment

                value = new_value - self.increment

            wx.CallAfter(self.SetValue, value)

        evt.Skip()

    def _on_size(self, evt):
        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)
        evt.Skip()

    def _run_startup(self, value):
        event = threading.Event()

        for i in range(1, 101):
            self.SetValue(float(i))
            event.wait(0.005)

        for i in range(99, -1, -1):
            self.SetValue(float(i))
            event.wait(0.005)

        for i in range(0, int(round(value)) + 1):
            self.SetValue(float(i))
            event.wait(0.005)

        self.SetValue(value)

    @property
    def _ticks(self):
        width, height = self.GetSize()
        center = min(width, height) / 2

        center_x = width / 2
        center_y = height / 2

        radius1 = center - 2
        radius2 = radius1 - 3
        radius3 = radius2 - 2
        ticks = []

        pens = []

        for i in range(0, 101):

            if i <= self.value:
                if i <= 75:
                    pen = self.green_pen
                elif i <= 90:
                    pen = self.yellow_pen
                else:
                    pen = self.red_pen
            else:
                pen = self.black_pen

            degree = _remap(i, 0.0, 100.0, 135, 405)
            radian = math.radians(degree)
            cos = math.cos(radian)
            sin = math.sin(radian)

            if not i % 10:
                x1 = center_x + int(round(radius1 * cos))
                y1 = center_y + int(round(radius1 * sin))
            else:
                x1 = center_x + int(round(radius2 * cos))
                y1 = center_y + int(round(radius2 * sin))

            x2 = center_x + int(round(radius3 * cos))
            y2 = center_y + int(round(radius3 * sin))

            ticks += [[x1, y1, x2, y2]]

            pens += [pen]

        return ticks, pens

    def OnPaint(self, _):
        ticks, pens = self._ticks

        neon_colour = pens[int(self.value)].GetColour().Get()

        client_rect = self.GetClientRect()
        boundary_rect = client_rect

        client_x, client_y, client_width, client_height = client_rect

        radius = (
            min(boundary_rect.GetWidth(), boundary_rect.GetHeight()) // 2
        ) * 0.85

        radius_smaller = radius * 0.80

        x_center = client_x + client_width // 2
        y_center = client_y + client_height // 2

        knob_radius = radius * 0.345 * 2

        knob_degree = _remap(self.value, 0.0, 100.0, 135.0, 405.0)
        knob_radian = math.radians(knob_degree)

        cos = math.cos(knob_radian)
        sin = math.sin(knob_radian)

        knob_x = x_center + int(round(knob_radius * cos))
        knob_y = y_center + int(round(knob_radius * sin))
        knob_radius = radius * 0.04

        # I had an issue with the image being rendered when the widget was
        # first created. and also during sizing events. Sometimes the image
        # would not get drawn.
        # To solve this problem rendering onto a bitmap and then drawing the
        # bitmap seems to have solved the issue.
        bmp = wx.EmptyBitmapRGBA(
            client_width,
            client_height,
            *self.GetBackgroundColour().Get()
        )

        # Memory DC for loading of the bitmap so we can draw onto it.
        dc = wx.MemoryDC()
        # select the bitmap to draw onto
        dc.SelectObject(bmp)
        # create a graphics context so we can create custom gradient brushes
        gc = wx.GraphicsContext.Create(dc)

        def draw_circle(x, y, r):
            gc.DrawEllipse(x - r, y - r, r * 2, r * 2)

        gc.SetBrush(wx.TRANSPARENT_BRUSH)

        # neon ring around volume knob
        neon_radius = radius - 1
        for i in range(0, 50):
            alpha = 255 - (i * 30)

            if alpha < 0:
                break

            colour = wx.Colour(*neon_colour[:-1] + (alpha,))

            gc.SetPen(wx.Pen(colour, 1))
            draw_circle(x_center, y_center, neon_radius + i)

        gc.SetPen(wx.TRANSPARENT_PEN)

        # outside ring of volume knob
        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                x_center,
                y_center - radius,
                x_center,
                y_center - radius,
                radius * 2,
                wx.WHITE,
                wx.Colour(33, 33, 33)
            )
        )

        draw_circle(x_center, y_center, radius)

        # inside of volume knob
        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                x_center,
                y_center + radius_smaller,
                x_center,
                y_center + radius_smaller,
                radius_smaller * 2,
                wx.WHITE,
                wx.Colour(33, 33, 33)
            )
        )

        draw_circle(x_center, y_center, radius_smaller)

        # handle of the volume knob
        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                knob_x,
                knob_y + knob_radius,
                knob_x,
                knob_y + knob_radius,
                knob_radius * 2,
                wx.WHITE,
                wx.Colour(33, 33, 33)
            )
        )

        draw_circle(knob_x, knob_y, knob_radius)

        # create a GCDC. this provides a better quality to the tick marks
        # when they are drawn.
        gcdc = wx.GCDC(gc)
        gcdc.SetBrush(wx.TRANSPARENT_BRUSH)

        # draw the tick marks
        gcdc.DrawLineList(ticks, pens)

        # release the bmp from the DC
        dc.SelectObject(wx.EmptyBitmap(1, 1))

        # destroy and delete the GCDC
        gcdc.Destroy()
        del gcdc

        # destroy and delete the DC
        dc.Destroy()
        del dc

        # create a buffered paint dc to draw the bmp to the client area
        pdc = wx.BufferedPaintDC(self)
        pdc.DrawBitmap(bmp, 0, 0)

        if isinstance(self._startup, (int, float)):
            self._startup = threading.Thread(
                target=self._run_startup,
                args=(self._startup,)
            )
            self._startup.daemon = True
            self._startup.run()


if __name__ == '__main__':
    class Frame(wx.Frame):

        def __init__(self):

            wx.Frame.__init__(self, None, -1, size=(400, 400))

            ctrl = VolumeCtrl(self, value=25.0)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(ctrl, 1, wx.EXPAND | wx.ALL, 10)

            self.SetSizer(sizer)


    app = wx.App()

    frame = Frame()
    frame.Show()
    app.MainLoop()
