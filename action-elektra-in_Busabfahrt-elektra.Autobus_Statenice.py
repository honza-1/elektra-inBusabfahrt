#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import requests
import re
from htmldom import htmldom

URL = "http://jizdnirady.idnes.cz/pid/spojeni/"

PARAMS =  {'f': 'Statenice','t': 'Borislavka','fc':'301003','tc':'301003','submit':'true'}

def subscribe_intent_callback(hermes, intentMessage):
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    r = requests.get(url=URL, params=PARAMS)
    dom = htmldom.HtmlDom().createDom(r.text)
    a = dom.find("th[class~=time]")
    hermes.publish_end_session(intend_message.session_id,"Der Bus fährt um "+a[0].text()+" und dann um "+a[1].text())
    
if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("elektra:in_Busabfahrt", subscribe_intent_callback) \
         .start()
