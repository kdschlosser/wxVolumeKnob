# -*- coding: utf-8 -*-
import wx
import math
import threading


def frange(start, stop=None, step=1.0):
    """
    Range function that accepts floats
    """

    start = float(start)
    step = float(step)

    if stop is None:
        stop, start = start, 0.0

    count = int(math.ceil(stop - start) / step)
    return iter(start + (n * step) for n in range(count))


def _remap(value, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min

    try:
        return (
            (((value - old_min) * new_range) / old_range) + new_min
        )
    except ZeroDivisionError:
        return new_min


class Handler(object):

    def __init__(self):
        self._size = None
        self._tick_list = None
        self._value = None
        self._min_value = None
        self._max_value = None
        self._thumb_multiplier = 0.04
        self._thumb_position = None
        self._thumb_radius = None
        self._radius = None
        self._thumb_orbit = None
        self._neon_radius = None
        self._neon_colour = None
        self._foreground_colour = None
        self._background_colour = None
        self._tick_pens = []
        self._tick_ranges = []
        self._tick_range_colours = []
        self._default_tick_pen = None
        self._tick_frequency = 2.0
        self._increment = 1.0
        self._secondary_colour = wx.WHITE
        self._primary_colour = wx.Colour(33, 33, 33)
        self._page_size = None
        self._glow = False
        self._depression = False
        self._thumb_glow = False
        self._ticks = False
        self._shadow = False

    @property
    def shadow(self):
        return self._shadow

    @shadow.setter
    def shadow(self, value):
        self._shadow = value

    @property
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, value):
        self._glow = value

    @property
    def depression(self):
        return self._depression

    @depression.setter
    def depression(self, value):
        self._depression = value

    @property
    def thumb_glow(self):
        return self._thumb_glow

    @thumb_glow.setter
    def thumb_glow(self, value):
        self._thumb_glow = value

    @property
    def primary_colour(self):
        return self._primary_colour

    @primary_colour.setter
    def primary_colour(self, value):
        self._primary_colour = value

    @property
    def secondary_colour(self):
        return self._secondary_colour

    @secondary_colour.setter
    def secondary_colour(self, value):
        self._secondary_colour = value

    @property
    def foreground_colour(self):
        return self._foreground_colour

    @foreground_colour.setter
    def foreground_colour(self, value):
        self._tick_list = None
        self._default_tick_pen = wx.Pen(value, 2)
        self._foreground_colour = value

    @property
    def background_colour(self):
        return self._background_colour

    @background_colour.setter
    def background_colour(self, value):
        self._background_colour = value

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        self._min_value = value

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self._max_value = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._radius = None
        self._thumb_radius = None
        self._neon_radius = None
        self._thumb_orbit = None
        self._thumb_position = None
        self._tick_list = None
        self._size = value

    @property
    def center(self):
        width, height = self.size

        return int(width / 2), int(height / 2)

    @property
    def radius(self):
        if self._radius is None:
            width, height = self.size
            radius = (min(width, height) // 2) * 0.75
            self._radius = radius

        return self._radius

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._thumb_position = None
        self._tick_list = None
        self._value = value

    @property
    def neon_radius(self):
        if self._neon_radius is None:
            radius = self.radius
            self._neon_radius = radius - 1

        return self._neon_radius

    @property
    def thumb_multiplier(self):
        return self._thumb_multiplier

    @thumb_multiplier.setter
    def thumb_multiplier(self, value):
        self._thumb_radius = None
        self._thumb_orbit = None
        self._thumb_position = None
        self._thumb_multiplier = value

    @property
    def thumb_radius(self):
        if self._thumb_radius is None:
            radius = self.radius
            self._thumb_radius = radius * self.thumb_multiplier

        return self._thumb_radius

    @property
    def thumb_orbit(self):
        if self._thumb_orbit is None:
            radius = self.radius
            center_radius = self.center_radius
            self._thumb_orbit = int(round((radius - center_radius) / 2.0)) + center_radius

        return self._thumb_orbit

    @property
    def neon_colour(self):
        colour = self._neon_colour
        colours = self.tick_range_colors

        for i, r_value in enumerate(self.tick_ranges):
            if r_value < self.value:
                try:
                    colour = colours[i + 1]
                except IndexError:
                    break

        if isinstance(colour, wx.Colour):
            colour = colour.Get(False)

        if len(colour) == 4:
            colour = colour[:-1]

        return colour

    @property
    def center_radius(self):
        thumb_radius = self.thumb_radius

        return self.radius - (thumb_radius * 2) - (self.radius * 0.1)

    @property
    def thumb_position(self):
        if self._thumb_position is None:
            width, height = self.size

            x_center = width // 2
            y_center = height // 2

            thumb_orbit = self.thumb_orbit
            thumb_degree = _remap(self.value, self.min_value, self.max_value, 135.0, 405.0)
            thumb_radian = math.radians(thumb_degree)

            cos = math.cos(thumb_radian)
            sin = math.sin(thumb_radian)

            thumb_x = x_center + int(round(thumb_orbit * cos))
            thumb_y = y_center + int(round(thumb_orbit * sin))

            self._thumb_position = (thumb_x, thumb_y)

        return self._thumb_position

    @property
    def tick_pens(self):
        return self._tick_pens

    @property
    def tick_range_colors(self):
        return self._tick_range_colours

    @tick_range_colors.setter
    def tick_range_colors(self, value):
        del self._tick_pens[:]

        for colour in value:
            self._tick_pens += [wx.Pen(colour, 1)]

        self._tick_list = None
        self._tick_range_colours = value

    @property
    def tick_ranges(self):
        return self._tick_ranges

    @tick_ranges.setter
    def tick_ranges(self, value):
        self._tick_list = None
        self._tick_ranges = value

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def tick_frequency(self):
        return self._tick_frequency

    @tick_frequency.setter
    def tick_frequency(self, value):
        self._tick_frequency = value

    @property
    def page_size(self):
        if self._page_size is None:
            return (self.max_value - self.min_value) / 10.0
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value
        self._tick_list = None

    @property
    def ticks(self):
        return self._ticks

    @ticks.setter
    def ticks(self, value):
        self._ticks = value

    @property
    def tick_list(self):
        if self._tick_list is None:

            width, height = self.size
            center = int(round(min(width, height) / 2.0))

            center_x = int(round(width / 2.0))
            center_y = int(round(height / 2.0))

            large_outside_radius = center - int(round(center * 0.05))
            inside_radius = int(round(large_outside_radius * 0.90))
            small_outside_radius = int(round(self.radius * 1.20))

            ticks = []

            tick_pens = self.tick_pens
            num_small_ticks = int(round((self.max_value - self.min_value) / self.tick_frequency)) + 1
            num_large_ticks = int(round((self.max_value - self.min_value) / self.page_size)) + 1
            num_small_ticks -= num_large_ticks

            large_tick_frequency = (num_large_ticks - 1) * self.increment

            pen_size = max(1.0, (center * 0.015) - (num_small_ticks / 100.0))

            print

            for i in frange(self.min_value, self.max_value + self.increment, self.increment):
                if i % self.tick_frequency:
                    continue

                if i <= self.value:
                    for pen_num, tick_range in enumerate(self.tick_ranges):
                        if i <= tick_range:
                            if pen_num < len(tick_pens):
                                pen = tick_pens[pen_num]
                            else:
                                pen = self._default_tick_pen

                            self._neon_colour = pen.GetColour().Get(False)
                            break
                    else:
                        pen = self._default_tick_pen
                else:
                    pen = self._default_tick_pen

                pen.SetWidth(pen_size)
                degree = _remap(i, self.min_value, self.max_value, 135.0, 405.0)
                radian = math.radians(degree)
                cos = math.cos(radian)
                sin = math.sin(radian)

                x2 = center_x + int(round(inside_radius * cos))
                y2 = center_y + int(round(inside_radius * sin))

                if i % large_tick_frequency:
                    x1 = center_x + int(round(small_outside_radius * cos))
                    y1 = center_y + int(round(small_outside_radius * sin))
                else:
                    x1 = center_x + int(round(large_outside_radius * cos))
                    y1 = center_y + int(round(large_outside_radius * sin))

                ticks += [[i, pen, [x1, y1, x2, y2]]]
            self._tick_list = ticks

        return self._tick_list

    def _get_tick_number(self, value):
        value_range = self.max_value + self.increment - self.min_value
        num_ticks = value_range * self.tick_frequency

        tick_num = _remap(value, self.min_value, self._max_value, 0, num_ticks)
        return int(tick_num)

    def is_value_line_up(self, value):
        if value < self.value:
            return False

        ticks = self.tick_list

        for i, (v, pen, coords) in enumerate(ticks):
            if v == value:
                break
        else:
            return False

        if i == len(ticks) - 1:
            return False
        if ticks[i + 1][2] != coords:
            return True

        return False

    def is_value_line_down(self, value):
        if value > self.value:
            return False
        ticks = self.tick_list

        for i, (v, pen, coords) in enumerate(ticks):
            if v == value:
                break
        else:
            return False

        if i == 0:
            return False
        if ticks[i - 1][2] != coords:
            return True

        return False

    def is_page(self, value):
        if value % self.page_size:
            return False
        return True


class KnobEvent(wx.PyCommandEvent):
    """
    Wrapper around wx.ScrollEvent to allow the GetPosition and SetPosition
    to accept floats
    """

    def __init__(self, event_type, id=1):
        wx.PyCommandEvent.__init__(self, event_type, id)

        self.__orientation = None
        self.__position = 0

    def SetPosition(self, value):
        self.__position = value

    def GetPosition(self):
        return self.__position

    def SetOrientation(self, value):
        self.__orientation = value

    def GetOrientation(self):
        return self.__orientation

    def GetEventUserData(self):
        return None

    Position = property(fget=GetPosition, fset=SetPosition)
    Orientation = property(fget=GetOrientation, fset=SetOrientation)


KNOB_GLOW = 2 ** 2
KNOB_DEPRESSION = 3 ** 2
KNOB_HANDLE_GLOW = 4 ** 2
KNOB_TICKS = 5 ** 2
KNOB_SHADOW = 6 ** 2

DefaultKnobStyle = KNOB_GLOW | KNOB_DEPRESSION | KNOB_HANDLE_GLOW | KNOB_TICKS | KNOB_SHADOW
KnobNameStr = 'Knob Control'


# noinspection PyPep8Naming
class KnobCtrl(wx.Control):

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=0.0,
        minValue=0.0,
        maxValue=100.0,
        increment=1.0,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=0,
        name=KnobNameStr,
        knobStyle=DefaultKnobStyle
    ):

        wx.Control.__init__(
            self,
            parent,
            id=id,
            pos=pos,
            size=size,
            style=style | wx.BORDER_NONE,
            name=name
        )

        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.increment = increment
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._on_mouse_lost_capture)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._handler = Handler()
        self._handler.value = value
        self._handler.min_value = minValue
        self._handler.max_value = maxValue
        self._handler.increment = increment
        self._handler.background_colour = parent.GetBackgroundColour()
        self._handler.foreground_colour = parent.GetForegroundColour()
        self._last_degrees = None
        self._startup = False

        self._handler.size = self.GetBestSize()

        self._handler.glow = bool(knobStyle & KNOB_GLOW)
        self._handler.depression = bool(knobStyle & KNOB_DEPRESSION)
        self._handler.thumb_glow = bool(knobStyle & KNOB_HANDLE_GLOW)
        self._handler.ticks = bool(knobStyle & KNOB_TICKS)
        self._handler.shadow = bool(knobStyle & KNOB_SHADOW)

        self._knob_style = knobStyle

    def HasGlow(self):
        return self._handler.glow

    def HasDepression(self):
        return self._handler.depression

    def HasHandleGlow(self):
        return self._handler.thumb_glow

    def HasTicks(self):
        return self._handler.ticks

    def HasShadow(self):
        return self._handler.shadow

    def GetKnobStyle(self):
        return self._knob_style

    def SetKnobStyle(self, knobStyle):
        self._handler.glow = bool(knobStyle & KNOB_GLOW)
        self._handler.depression = bool(knobStyle & KNOB_DEPRESSION)
        self._handler.thumb_glow = bool(knobStyle & KNOB_HANDLE_GLOW)
        self._handler.ticks = bool(knobStyle & KNOB_TICKS)
        self._handler.shadow = bool(knobStyle & KNOB_SHADOW)

        self._knob_style = knobStyle

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def GetPageSize(self):
        return self._handler.page_size

    def SetPageSize(self, value):
        if (self._handler.max_value - self._handler.min_value) % value:
            raise RuntimeError(
                'Page size needs to be a multiple of the value range (maxValue - minValue = valueRange)'
            )
        self._handler.page_size = value

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def GetValueRange(self):
        return self._handler.min_value, self._handler.max_value

    def SetValueRange(self, minValue, maxValue):
        self._handler.min_value = minValue
        self._handler.max_value = maxValue

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def _create_event(self, event, value):
        """
        Internal use, creates a new KnobEvent
        :param event: wx event.
        :return: None
        """
        event = KnobEvent(event, self.GetId())
        event.SetId(self.GetId())
        event.SetEventObject(self)
        event.SetPosition(value)
        event.SetOrientation(wx.HORIZONTAL)
        self.GetEventHandler().ProcessEvent(event)

    def _on_char_hook(self, evt):

        key_code = evt.GetKeyCode()

        if key_code in (wx.WXK_PAGEUP, wx.WXK_NUMPAD_PAGEUP):
            value = self._handler.value + self._handler.page_size
            value -= value % self._handler.page_size

            event = None

        elif key_code in (wx.WXK_PAGEDOWN, wx.WXK_NUMPAD_PAGEDOWN):
            value = self._handler.value - (self._handler.value % self._handler.page_size)

            if value == self._handler.value:
                value -= self._handler.page_size

            event = None

        elif key_code in (
            wx.WXK_UP,
            wx.WXK_ADD,
            wx.WXK_NUMPAD_UP,
            wx.WXK_NUMPAD_ADD
        ):
            event = wx.wxEVT_SCROLL_LINEUP
            value = self._handler.value + self._handler.increment

        elif key_code in (
            wx.WXK_DOWN,
            wx.WXK_SUBTRACT,
            wx.WXK_NUMPAD_DOWN,
            wx.WXK_NUMPAD_SUBTRACT
        ):
            event = wx.wxEVT_SCROLL_LINEDOWN
            value = self._handler.value - self._handler.increment

        elif key_code in (wx.WXK_HOME, wx.WXK_NUMPAD_HOME):
            value = self._handler.min_value
            event = None

        elif key_code in (wx.WXK_END, wx.WXK_NUMPAD_END):
            value = self._handler.max_value
            event = None

        # numbers that represent 10% incremnts of the value range
        elif key_code - 48 in list(range(0, 10)):
            percent = (key_code - 48) * 0.1
            value_range = self._handler.max_value - self._handler.min_value
            value = value_range * percent

            value += value % self._handler.increment
            event = None

        else:
            evt.Skip()
            return

        self._last_degrees = None
        self.__generate_events(event, value)

        evt.Skip()

    def _on_erase_background(self, _):
        pass

    def _on_mouse_lost_capture(self, evt):
        self._last_degrees = None
        self.ReleaseMouse()
        self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
        self._create_event(wx.wxEVT_SCROLL_THUMBRELEASE, self.GetValue())
        self.Refresh()
        self.Update()
        evt.Skip()

    def __generate_events(self, event, value, degrees=None):

        if value >= self._handler.max_value:
            value = self._handler.max_value

        elif value <= self._handler.min_value:
            value = self._handler.min_value

        if value != self._handler.value:
            self._last_degrees = degrees
            handler_value = self._handler.value
            self._handler.value = value

            def _do():
                self.Refresh()
                self.Update()

            wx.CallAfter(_do)

            if event is not None:
                self._create_event(event, value)

            if self._handler.is_page(value):
                if value > handler_value:
                    self._create_event(wx.wxEVT_SCROLL_PAGEUP, value)
                else:
                    self._create_event(wx.wxEVT_SCROLL_PAGEDOWN, value)

            if value == self._handler.max_value:
                self._create_event(wx.wxEVT_SCROLL_TOP, value)
            elif value == self._handler.min_value:
                self._create_event(wx.wxEVT_SCROLL_BOTTOM, value)

            self._create_event(wx.wxEVT_SCROLL_CHANGED, value)

            return True

        return False

    def _on_mouse_wheel(self, evt):
        wheel_delta = evt.GetWheelRotation()
        value = self._handler.value

        if wheel_delta < 0:
            value -= self._handler.increment
            event = wx.wxEVT_SCROLL_LINEDOWN

        elif wheel_delta > 0:
            value += self._handler.increment
            event = wx.wxEVT_SCROLL_LINEUP

        else:
            evt.Skip()
            return

        self.__generate_events(event, value)

        evt.Skip()

    def _on_mouse_left_up(self, evt):

        if self.HasCapture():
            self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
            self.ReleaseMouse()
            self._create_event(wx.wxEVT_SCROLL_THUMBRELEASE, self.GetValue())
            self.Refresh()
            self.Update()

        evt.Skip()

    def _on_mouse_left_down(self, evt):
        thumb_x, thumb_y = self._handler.thumb_position
        thumb_radius = self._handler.thumb_radius

        start_x = thumb_x - thumb_radius
        start_y = thumb_y - thumb_radius
        end_x = thumb_x + thumb_radius
        end_y = thumb_y + thumb_radius

        x, y = evt.GetPosition()

        if start_x <= x <= end_x and start_y <= y <= end_y:
            self.CaptureMouse()
            self.Bind(wx.EVT_MOTION, self._on_mouse_move)

        evt.Skip()

    def _on_mouse_move(self, evt):

        if self.HasCapture():
            thumb_x, thumb_y = self._handler.thumb_position
            thumb_radius = self._handler.thumb_radius

            start_x = thumb_x - (thumb_radius * 8)
            start_y = thumb_y - (thumb_radius * 8)
            end_x = thumb_x + (thumb_radius * 8)
            end_y = thumb_y + (thumb_radius * 8)

            x, y = evt.GetPosition()

            if start_x >= x or end_x <= x or start_y >= y or end_y <= y:
                self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
                self.ReleaseMouse()
                self._create_event(wx.wxEVT_SCROLL_THUMBRELEASE, self.GetValue())
                self.Refresh()
                self.Update()

                evt.Skip()
                return

            width, height = self.GetSize()
            center_x = width / 2.0
            center_y = height / 2.0

            radians = math.atan2(y - center_y, x - center_x)

            degrees = math.degrees(radians)
            if degrees < 90:
                degrees += 360

            value = _remap(degrees, 135.0, 405.0, self._handler.min_value, self._handler.max_value)

            if (value % self._handler.increment) * 2 >= self._handler.increment:
                if self._last_degrees < degrees:
                    value -= (value % self._handler.increment)
                    event = wx.wxEVT_SCROLL_LINEUP

                elif self._last_degrees > degrees:
                    value -= (value % self._handler.increment)
                    event = wx.wxEVT_SCROLL_LINEDOWN
                else:
                    self._last_degrees = degrees
                    evt.Skip()
                    return
            else:
                self._last_degrees = degrees
                evt.Skip()
                return

            if self.__generate_events(event, value, degrees):
                self._create_event(wx.wxEVT_SCROLL_THUMBTRACK, value)

        evt.Skip()

    def _on_size(self, evt):
        width, height = evt.GetSize()
        self._handler.size = (width, height)

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)
        evt.Skip()

    def RunStartupAnimation(self):
        if self._startup is False:
            self._startup = True

    def GetPrimaryColour(self):
        return self._handler.primary_colour

    def SetPrimaryColour(self, value):

        if isinstance(value, (list, tuple)):
            value = wx.Colour(*value)

        self._handler.primary_colour = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetSecondaryColour(self):
        return self._handler.secondary_colour

    def SetSecondaryColour(self, value):

        if isinstance(value, (list, tuple)):
            value = wx.Colour(*value)

        self._handler.secondary_colour = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickFrequency(self):
        return self._handler.tick_frequency

    def SetTickFrequency(self, value):
        value_range = self._handler.max_value - self._handler.min_value
        if value_range % value:
            raise RuntimeError('tick frequency must be a multiple of the value range')

        self._handler.tick_frequency = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetThumbSize(self):
        return int(self._handler.thumb_multiplier * 100)

    def SetThumbSize(self, value):
        value /= 100.0

        self._handler.thumb_multiplier = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickColours(self):
        return self._handler.tick_range_colors

    def SetTickColours(self, values):

        colours = []

        for colour in values:
            if isinstance(colour, (list, tuple)):
                colour = wx.Colour(*colour)

            colours += [colour]

        self._handler.tick_range_colors = colours

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickColorRanges(self):
        return self._handler.tick_ranges

    def SetTickColourRanges(self, values):
        self._handler.tick_ranges = values

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def SetSize(self, size):
        wx.Control.SetSize(self, size)
        width, height = self.GetSize()
        self._handler.size = (width, height)

    def GetValue(self):
        return self._handler.value

    def SetValue(self, value):
        self._last_degrees = None

        if self._handler.min_value > value:
            raise ValueError('new value is lower then the set minimum')
        if self._handler.max_value < value:
            raise ValueError('new value is higher then the set maximum')

        self._handler.value = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetIncrement(self):
        return self._handler.increment

    def SetIncrement(self, increment):
        self._handler.increment = increment

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetMinValue(self):
        return self._handler.min_value

    def SetMinValue(self, value):
        self._handler.min_value = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetMaxValue(self):
        return self._handler.max_value

    def SetMaxValue(self, value):
        self._handler.max_value = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def _run_startup(self):
        value = self._handler.value
        event = threading.Event()

        for i in frange(
                value,
                self._handler.max_value + self._handler.increment,
                self._handler.increment
        ):
            self.SetValue(i)
            event.wait(0.02)

        for i in frange(
                self._handler.max_value,
                self._handler.min_value - self._handler.increment,
                -self._handler.increment
        ):
            self.SetValue(i)
            event.wait(0.02)

        for i in frange(
                self._handler.min_value,
                value + self._handler.increment,
                self._handler.increment
        ):
            self.SetValue(i)
            event.wait(0.02)

    def OnPaint(self, _):

        width, height = self._handler.size

        if width <= 0 or height <= 0:
            bmp = wx.EmptyBitmapRGBA(
                1,
                1
            )
            pdc = wx.PaintDC(self)
            gcdc = wx.GCDC(pdc)
            gcdc.DrawBitmap(bmp, 0, 0)

            gcdc.Destroy()
            del gcdc

            self._startup = None
            return

        bmp = wx.EmptyBitmapRGBA(
            width,
            height
        )

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(dc)
        gcdc = wx.GCDC(gc)

        gcdc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        gcdc.SetPen(wx.TRANSPARENT_PEN)

        gcdc.DrawRectangle(0, 0, width, height)

        def draw_circle(x, y, r, _gcdc):
            _gcdc.DrawEllipse(
                int(round(float(x) - r)),
                int(round(float(y) - r)),
                int(round(r * 2.0)),
                int(round(r * 2.0))
            )

        gcdc.SetBrush(wx.TRANSPARENT_BRUSH)
        x_center, y_center = self._handler.center

        gcdc.SetPen(wx.TRANSPARENT_PEN)
        radius = self._handler.radius

        if self._handler.shadow:
            # shadow
            stops = wx.GraphicsGradientStops()
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.45))
            stops.Add(wx.GraphicsGradientStop(wx.Colour(0, 0, 0, 255), 0.25))

            stops.SetStartColour(wx.Colour(0, 0, 0, 255))
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center + (radius * 0.10),
                    y_center + (radius * 0.10),
                    x_center + (radius * 0.30),
                    y_center + (radius * 0.30),
                    radius * 2.3,
                    stops
                )
            )

            draw_circle(x_center + (radius * 0.10), y_center + (radius * 0.10), radius * 2, gcdc)

            # eliminate any shadow under the knob just in case there is a color
            # used in the gradient of the knob that does not have an alpha level of 255

            gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
            draw_circle(x_center, y_center, radius - 2, gcdc)

        if self._handler.glow:
            _ = self._handler.tick_list
            neon_colour = self._handler.neon_colour

            stops = wx.GraphicsGradientStops()

            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.265))
            stops.Add(wx.GraphicsGradientStop(wx.Colour(*neon_colour + (255,)), 0.25))
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.248))

            stops.SetStartColour(wx.TransparentColour)
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center,
                    y_center,
                    x_center,
                    y_center,
                    radius * 4,
                    stops
                )
            )

            draw_circle(x_center, y_center, radius * 2, gcdc)

        # outside ring of volume knob

        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                x_center - radius,
                y_center - radius,
                x_center,
                y_center - radius,
                radius * 2,
                self._handler.secondary_colour,
                self._handler.primary_colour

            )
        )

        draw_circle(x_center, y_center, radius, gcdc)

        thumb_x, thumb_y = self._handler.thumb_position
        thumb_radius = self._handler.thumb_radius

        # inside of volume knob
        if self._handler.depression:
            center_radius = self._handler.center_radius
            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center + center_radius,
                    y_center + center_radius,
                    x_center,
                    y_center + center_radius,
                    center_radius * 2,
                    self._handler.secondary_colour,
                    self._handler.primary_colour
                )
            )

            draw_circle(x_center, y_center, center_radius, gcdc)

        if self._last_degrees is None:
            self._last_degrees = _remap(
                self._handler.value,
                self._handler.min_value,
                self._handler.max_value,
                135.0,
                405.0
            )

        # handle of the volume knob
        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                thumb_x + thumb_radius,
                thumb_y + thumb_radius,
                thumb_x,
                thumb_y + thumb_radius,
                thumb_radius * 2,
                self._handler.secondary_colour,
                self._handler.primary_colour
            )
        )

        draw_circle(thumb_x, thumb_y, thumb_radius, gcdc)

        if self._handler.thumb_glow:
            _ = self._handler.tick_list
            neon_colour = self._handler.neon_colour

            stops = wx.GraphicsGradientStops()

            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.355))
            stops.Add(wx.GraphicsGradientStop(wx.Colour(*neon_colour + (255,)), 0.28))
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.258))

            stops.SetStartColour(wx.TransparentColour)
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    thumb_x,
                    thumb_y,
                    thumb_x,
                    thumb_y,
                    thumb_radius * 4,
                    stops
                )
            )

            draw_circle(thumb_x, thumb_y, thumb_radius * 2, gcdc)

        gcdc.SetBrush(wx.TRANSPARENT_BRUSH)

        # draw the tick marks
        if self._handler.ticks:
            ticks = []
            pens = []
            for _, pen, coords in self._handler.tick_list:
                ticks += [coords]
                pens += [pen]

            gcdc.DrawLineList(ticks, pens)

        dc.SelectObject(wx.EmptyBitmap(1, 1))
        gcdc.Destroy()
        del gcdc

        dc.Destroy()
        del dc

        # create a buffered paint dc to draw the bmp to the client area
        pdc = wx.PaintDC(self)
        gcdc = wx.GCDC(pdc)
        gcdc.DrawBitmap(bmp, 0, 0)

        gcdc.Destroy()
        del gcdc

        if self._startup is True:
            self._startup = None
            t = threading.Thread(target=self._run_startup)
            t.daemon = True
            t.start()
        else:
            self._startup = None


if __name__ == '__main__':
    EVENT_MAPPING = {
        wx.EVT_SCROLL_TOP.typeId: 'EVT_SCROLL_TOP',
        wx.EVT_SCROLL_BOTTOM.typeId: 'EVT_SCROLL_BOTTOM',
        wx.EVT_SCROLL_LINEUP.typeId: 'EVT_SCROLL_LINEUP',
        wx.EVT_SCROLL_LINEDOWN.typeId: 'EVT_SCROLL_LINEDOWN',
        wx.EVT_SCROLL_PAGEUP.typeId: 'EVT_SCROLL_PAGEUP',
        wx.EVT_SCROLL_PAGEDOWN.typeId: 'EVT_SCROLL_PAGEDOWN',
        wx.EVT_SCROLL_THUMBTRACK.typeId: 'EVT_SCROLL_THUMBTRACK',
        wx.EVT_SCROLL_THUMBRELEASE.typeId: 'EVT_SCROLL_THUMBRELEASE',
        wx.EVT_SCROLL_CHANGED.typeId: 'EVT_SCROLL_CHANGED'
    }


    class Frame(wx.Frame):

        def __init__(self):

            wx.Frame.__init__(self, None, -1, size=(400, 400))

            sizer = wx.BoxSizer(wx.VERTICAL)
            ctrl = KnobCtrl(self, value=0.0, minValue=0.0, maxValue=100.0, increment=1.0)
            ctrl.SetThumbSize(7)
            ctrl.SetTickFrequency(1.0)
            ctrl.SetTickColours([(0, 255, 0, 255), (255, 187, 0, 255), (255, 0, 0, 255)])
            ctrl.SetTickColourRanges([75.0, 90.0, 100.0])
            ctrl.SetBackgroundColour(wx.Colour(80, 80, 80))
            # ctrl.SetPrimaryColour((33, 36, 112, 255))
            ctrl.SetSecondaryColour((225, 225, 225, 255))
            ctrl.Bind(wx.EVT_SCROLL, self.on_event)
            sizer.Add(ctrl, 1, wx.EXPAND)

            ctrl.RunStartupAnimation()

            self.SetSizer(sizer)

        def on_event(self, event):
            print event

            print EVENT_MAPPING[event.GetEventType()], event.Position

    app = wx.App()

    frame = Frame()
    frame.Show()
    app.MainLoop()
