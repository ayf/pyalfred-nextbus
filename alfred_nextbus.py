#!/usr/bin/env python

import re
import sys
import nextbus
from alp import item
from alp import log

def display_all_agencies():
    log('display_all_agencies')
    agencies = nextbus.get_all_agencies()
    items = []
    for agency in agencies:
        items.append(item.Item(title=agency.tag, subtitle=agency.title, valid=False, autocomplete=agency.tag))
    item.feedback(items)

def display_valid_systems_or_routes(agency_name):
    log('display_valid_systems_or_routes')
    items = []
    agencies = nextbus.get_all_agencies()
    tag = None
    for agency in agencies:
        if agency.tag == agency_name:
            tag = agency.tag
            break
        if re.search(agency_name, agency.tag):
            items.append(item.Item(title=agency.tag, subtitle=agency.title, valid=False, autocomplete=agency.tag))

    if not tag:
        item.feedback(items)
    else:
        routes = nextbus.get_all_routes_for_agency(tag)

        for route in routes:
            items.append(item.Item(title=route.tag, subtitle=route.title, valid=False, autocomplete='%s %s' % (tag, route.tag)))

        item.feedback(items)

def display_valid_routes_or_stops(system, route):
    log('display_valid_routes_or_stops')
    directions = nextbus.get_route_config(system, route).directions
    items = []
    for direction in directions:
        items.append(item.Item(title=direction.name, subtitle=direction.name, autocomplete='%s %s %s' % (system, route, direction.name)))
    item.feedback(items)


def display_valid_stops(system, route, route_direction):
    log('display_valid_stops')
    if not route_direction:
        return
    directions = nextbus.get_route_config(system, route).directions
    items = []
    for direction in directions:
        if direction.name == route_direction:
            found_route = direction
            break

    for stop in direction.stops:
        title = re.sub(' & ', ' and ', stop.title)
        items.append(item.Item(title=title, subtitle=direction.name, autocomplete='%s %s %s %s' % (system, route, route_direction, title)))

    item.feedback(items)

def display_valid_route_info(system, route, route_direction, stop_title):
    log('display_valid_route_info')
    log(stop_title)
    directions = nextbus.get_route_config(system, route).directions
    items = []
    route_ids = {}
    times = {}
    for direction in directions:
        if direction.name == route_direction:
            stops = direction.stops

    for stop in stops:
        if re.search(stop_title, stop.title):
            route_ids[stop.title] = stop.stop_id

    for stop_name, route_id in route_ids.iteritems():
        prediction = nextbus.get_predictions_for_stop(system, route_id)
        for p in prediction.predictions:
            if p.direction.route.tag == route:
                times.setdefault(stop_name, [])
                times[stop_name].append(str(p.minutes))

    for stop_name, times in times.iteritems():
        items.append(item.Item(title=stop_name, subtitle=' '.join(times)))

    item.feedback(items)

def parse_args(arg_list):
#    print arg_list
    for arg in arg_list:
        if not arg:
            return
#    print arg_list
#    display_valid_route_info(arg_list[0], arg_list[1], arg_list[2], re.sub(' and ', ' & ', ' '.join(arg_list[3:])))

    if len(arg_list) == 0:
        display_all_agencies()
    elif len(arg_list) == 1:
        display_valid_systems_or_routes(arg_list[0])
    elif len(arg_list) == 2:
        display_valid_routes_or_stops(arg_list[0], arg_list[1])
    elif len(arg_list) == 3:
        display_valid_stops(arg_list[0], arg_list[1], arg_list[2])
    elif len(arg_list) >= 4:
        display_valid_route_info(arg_list[0], arg_list[1], arg_list[2],
                re.sub(' and ', ' & ', ' '.join(arg_list[3:])))


def main():
    if len(sys.argv) > 1:
        parse_args(sys.argv[1].split(' '))
    else:
        parse_args([])

if __name__ == '__main__':
    main()

