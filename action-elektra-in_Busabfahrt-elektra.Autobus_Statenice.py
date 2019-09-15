#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import requests
import re
from htmldom import htmldom
from datetime import datetime, timedelta

URL = "http://jizdnirady.idnes.cz/pid/spojeni/"
PARAMS =  {'f': 'Statenice','t': 'Borislavka','fc':'301003','tc':'301003','submit':'true'}
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    if len(intentMessage.slots.Uhrzeit)!=0:
        dtti=intentMessage.slots.Uhrzeit.first().value
        today=datetime.now().date()
        tomorrow=today+timedelta(days=1)
        date_obj=datetime.strptime(dtti.split(' ')[0], "%Y-%m-%d").date()
        time_obj=dtti.split(' ')[1].split(':')[0]+":"+dtti.split(' ')[1].split(':')[1]
        PARAMS['time']=time_obj
        PARAMS['date']=date_obj.strftime("%d.%m.%Y")
        if date_obj==today:
              result_sentence="Heute nach "+time_obj+" Uhr fährt der Bus um "
        elif date_obj==tomorrow:
              result_sentence="Morgen nach "+time_obj+" Uhr fährt der Bus um "
        else:
              result_sentence="Am "+date_obj.strftime("%d.%m.%Y")+" nach "+time_obj+" Uhr fährt der Bus um "
    else:
        result_sentence="Der Bus fährt um "
    r = requests.get(url=URL,params=PARAMS)
    dom=htmldom.HtmlDom().createDom(r.text)
    a=dom.find("li[class=item]")
    result_sentence += a[0].text().split('\n')[0]+" Uhr und dann um "+a[1].text().split('\n')[0]+" Uhr"
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id,result_sentence)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("elektra:in_Busabfahrt", subscribe_intent_callback) \
         .start()
