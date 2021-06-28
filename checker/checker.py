#!/usr/bin/env python3
import time
import random
import string

import pwn

from ctf_gameserver import checkerlib

pwn.context.update(log_level="info")

class TreasuryChecker(checkerlib.BaseChecker):
    PORT = 6789
    DEBUG = False

    MENU_STRINGS = {
            'welcome' : b"Welcome to treasury!\n"
                        b"You got so much treasure that you can't\n"
                        b"store it all in one vault, but also don't\n"
                        b"to worry about keeping track of all the\n"
                        b"different ones? Let us worry about\n"
                        b"handling those while you focus on getting\n"
                        b"more!\n\n"
                        b"Choose an action:\n"
                        b"-> add treasure location\n"
                        b"-> view treasure locations\n"
                        b"-> update treasure location\n"
                        b"-> print logs\n"
                        b"-> quit\n"
                        b"  > ",
            'add_entry' : b"Give it a name: ",
            'add_desc' : b'Describe it: ',
            'add_end' : b"Great! We'll keep this information "
                        b"save for you! :)\n\n",
            'menu' : b"Choose an action:\n"
                     b"-> add treasure location\n"
                     b"-> view treasure locations\n"
                     b"-> update treasure location\n"
                     b"-> print logs\n"
                     b"-> quit\n"
                     b"  > ",
            'goodbye' : b"Goodbye!:)\n",
            'print_entry' : b"Logs are for admins only!\n"
                            b"Password: ",
            'print_end' : b"Nice try! :)\n"
                          b"But seriously: Logs are for admins ONLY!!\n\n",
            'update_entry' : b"Sorry, feature not yet implemented! \n"
                             b"Please wait for the next release.\n\n",
            'view_entry' : b'Location name: ',
            'view_desc' : b'\n-------------\nDescription: ',

            }

    def _generate_random_string(self, size):
        return ''.join(random.choice(string.ascii_letters) for x in range(size))

    def _get_key(self, flag):
        keys = checkerlib.load_state("keys")
        if not keys:
            keys = {}
        if flag in keys:
            return keys[flag]
        key = self._generate_random_string(60)
        while key in keys.values():
            key = self._generate_random_string(60)
        keys[flag] = key
        checkerlib.store_state("keys", keys)
        return key

    def _revoke_key(self, flag, key):
        keys = checkerlib.load_state("keys")
        if not keys:
            return
        if (flag in keys) and (key == keys[flag]):
            keys.pop(flag)
            checkerlib.store_state("keys", keys)


    def _add_treasure(self, key, value):
        try:
            if self.DEBUG:
                r = pwn.process("./treasury")
            else:
                r = pwn.remote(self.ip, self.PORT)
        except pwn.pwnlib.exception.PwnlibException:
            raise ConnectionRefusedError("Cannot connect to target")
        for i in range(9):
            # ascii art
            r.recvline()
        welcome_message = r.recvuntil("quit\n  > ")
        if welcome_message != self.MENU_STRINGS['welcome']:
            r.close()
            pwn.log.info("add_treasure: wrong welcome message")
            return 1
        pwn.log.info("add_treasure: checked welcome")
        r.sendline("add")

        resp = r.recvuntil("name: ")
        if resp != self.MENU_STRINGS['add_entry']:
            r.close()
            pwn.log.info("add_treasure: wrong add_entry message")
            return 1
        r.sendline(key)
        pwn.log.info("add_treasure: checked add_entry")

        resp = r.recvuntil("Describe it: ")
        if resp != self.MENU_STRINGS['add_desc']:
            r.close()
            pwn.log.info("add_treasure: wrong add_desc message")
            return 1
        r.sendline(value)
        pwn.log.info("add_treasure: checked add_desc")

        first = r.recv(numb=1)
        if first == b'T':
            r.close()
            pwn.log.info("add_treasure: key already in use")
            return 2
        elif first == b'W':
            r.close()
            pwn.log.info("add_treasure: save failed")
            return 3

        pwn.log.info("add_treasure: checked T")

        resp = r.recvuntil("save for you! :)\n\n")
        if first + resp != self.MENU_STRINGS['add_end']:
            r.close()
            pwn.log.info("add_treasure: wrong add_end message")
            return 1
        pwn.log.info("add_treasure: checked add_end")

        resp = r.recvuntil("quit\n  > ")
        if resp != self.MENU_STRINGS['menu']:
            r.close()
            pwn.log.info("add_treasure: wrong menu message")
            return 1
        r.sendline("quit")
        pwn.log.info("add_treasure: checked menu")

        resp = r.recvuntil("Goodbye!:)\n")
        if resp != self.MENU_STRINGS['goodbye']:
            r.close()
            pwn.log.info("add_treasure: wrong goodbye message")
            return 1
        pwn.log.info("add_treasure: checked goodbye")
        r.close()
        return 0

    def _view_treasure(self, key):
        try:
            if self.DEBUG:
                r = pwn.process("./treasury")
            else:
                r = pwn.remote(self.ip, self.PORT)
        except pwn.pwnlib.exception.PwnlibException:
            raise ConnectionRefusedError("Cannot connect to target")
        for i in range(9):
            # ascii art
            r.recvline()
        welcome_message = r.recvuntil("quit\n  > ")
        if welcome_message != self.MENU_STRINGS['welcome']:
            r.close()
            pwn.log.info("view_treasure: wrong welcome message")
            return None
        r.sendline("view")

        resp = r.recvuntil("Location name: ")
        if resp != self.MENU_STRINGS['view_entry']:
            r.close()
            pwn.log.info("view_treasure: wrong view_entry message")
            return None
        r.sendline(key)

        first = r.recv(numb=1)
        if first == b'N':
            r.close()
            pwn.log.info("view_treasure: no treasure found with this key")
            return None

        resp = r.recvuntil(key)
        if resp != key.encode():
            r.close()
            pwn.log.info("view_treasure: wrong key displayed")
            return None
        resp = r.recvuntil("Description: ")
        if resp != self.MENU_STRINGS['view_desc']:
            r.close()
            pwn.log.info("view_treasure: wrong view_desc message")
            return None
        desc = r.recvuntil("\n", drop=True)
        resp = r.recvuntil("\n")
        if resp != b'\n':
            r.close()
            pwn.log.info("view_treasure: missing newline")
            return None
        resp = r.recvuntil("quit\n  > ")
        if resp != self.MENU_STRINGS['menu']:
            r.close()
            pwn.log.info("view_treasure: wrong menu message")
            return None
        r.sendline("quit")
        resp = r.recvuntil("Goodbye!:)\n")
        if resp != self.MENU_STRINGS['goodbye']:
            r.close()
            pwn.log.info("view_treasure: wrong goodbye message")
            return None
        r.close()
        return desc

    def _update_location(self):
        try:
            if self.DEBUG:
                r = pwn.process("./treasury")
            else:
                r = pwn.remote(self.ip, self.PORT)
        except pwn.pwnlib.exception.PwnlibException:
            raise ConnectionRefusedError("Cannot connect to target")
        for i in range(9):
            # ascii art
            r.recvline()
        welcome_message = r.recvuntil("quit\n  > ")
        if welcome_message != self.MENU_STRINGS['welcome']:
            r.close()
            pwn.log.info("view_treasure: wrong welcome message")
            return False
        r.sendline("update")
        resp = r.recvuntil("for the next release.\n\n")
        if resp != self.MENU_STRINGS['update_entry']:
            r.close()
            pwn.log.info("view_treasure: wrong update_entry message")
            return False
        resp = r.recvuntil("quit\n  > ")
        if resp != self.MENU_STRINGS['menu']:
            r.close()
            pwn.log.info("view_treasure: wrong menu message")
            return False
        r.sendline("quit")

        resp = r.recvuntil("Goodbye!:)\n")
        if resp != self.MENU_STRINGS['goodbye']:
            r.close()
            pwn.log.info("view_treasure: wrong goodbye message")
            return False
        r.close()
        return True

    def _print_logs(self):
        try:
            if self.DEBUG:
                r = pwn.process("./treasury")
            else:
                r = pwn.remote(self.ip, self.PORT)
        except pwn.pwnlib.exception.PwnlibException:
            raise ConnectionRefusedError("Cannot connect to target")
        for i in range(9):
            # ascii art
            r.recvline()
        welcome_message = r.recvuntil("quit\n  > ")
        if welcome_message != self.MENU_STRINGS['welcome']:
            r.close()
            pwn.log.info("print_logs: wrong welcome message")
            return False
        r.sendline("print")
        resp = r.recvuntil("Password: ")
        if resp != self.MENU_STRINGS['print_entry']:
            r.close()
            pwn.log.info("print_logs: wrong print_entry message")
            return False
        pw = self._generate_random_string(8)
        r.sendline(pw)
        resp = r.recvuntil("ONLY!!\n\n")
        if resp != self.MENU_STRINGS['print_end']:
            r.close()
            pwn.log.info("print_logs: wrong print_end message")
            return False

        resp = r.recvuntil("quit\n  > ")
        if resp != self.MENU_STRINGS['menu']:
            r.close()
            pwn.log.info("print_logs: wrong menu message")
            return False
        r.sendline("quit")
        resp = r.recvuntil("Goodbye!:)\n")
        if resp != self.MENU_STRINGS['goodbye']:
            r.close()
            pwn.log.info("print_logs: wrong goodbye message")
            return False
        r.close()
        return True

    def place_flag(self, tick):
        start = time.time()

        flag = checkerlib.get_flag(tick)
        key = self._get_key(flag)

        ret = self._add_treasure(key, flag)
        if ret == 0:
            pwn.log.info(f"Placed flag {flag}")
            pwn.log.info(f"Overall duration for place_flag: {int(time.time() - start)}s")
            return checkerlib.CheckResult.OK
        if ret == 1:
            pwn.log.info("place_flag: add_treasure failed")
            pwn.log.info(f"Overall duration for place_flag: {int(time.time() - start)}s")
            return checkerlib.CheckResult.DOWN
        if ret == 3:
            return checkerlib.CheckResult.FAULTY

        while ret == 2:
            self._revoke_key(flag, key)
            key = self._get_key(flag)
            ret = self._add_treasure(key, flag)
            if ret == 0:
                pwn.log.info(f"Overall duration for place_flag: {int(time.time() - start)}s")
                return checkerlib.CheckResult.OK
            if ret == 1:
                pwn.log.info("place_flag: add_treasure failed")
                pwn.log.info(f"Overall duration for place_flag: {int(time.time() - start)}s")
                return checkerlib.CheckResult.DOWN

    def check_service(self):
        start = time.time()

        # add a location
        new_loc = self._generate_random_string(59)
        new_desc = self._generate_random_string(80)
        pwn.log.info(f"Trying to add location {new_loc}")
        ret = self._add_treasure(new_loc, new_desc)
        if ret == 1:
            pwn.log.info("check_service: add_treasure failed")
            pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
            return checkerlib.CheckResult.DOWN
        elif ret == 3:
            return checkerlib.CheckResult.FAULTY


        while ret == 2:
            new_loc = self._generate_random_string(59)
            ret = self._add_treasure(new_loc, new_desc)
            if ret == 0:
                break
            if ret == 1:
                pwn.log.info("check_service: add_treasure failed")
                pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
                return checkerlib.CheckResult.DOWN
        pwn.log.info("check_service: add_treasure OK")

        # check the location
        pwn.log.info(f"Trying to access location {new_loc}")
        remote_value = self._view_treasure(new_loc)
        if remote_value is None:
            pwn.log.info("check_service: view_treasure failed")
            pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
            return checkerlib.CheckResult.DOWN
        if remote_value.decode() != new_desc:
            pwn.log.info("check_service: view_treasure return wrong value")
            pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
            return checkerlib.CheckResult.FAULTY
        pwn.log.info("check_service: view_treasure OK")

        # try to update the location
        res = self._update_location()
        if not res:
            pwn.log.info("check_service: update_location failed")
            pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
            return checkerlib.CheckResult.FAULTY

        # "try" to access logs sometimes
        if random.choice([1,2]) == 2:
            pwn.log.info("Trying to access logs")
            res = self._print_logs()
            if not res:
                pwn.log.info("check_service: print_logs failed")
                pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
                return checkerlib.CheckResult.FAULTY
        else:
            pwn.log.info("Not trying to access logs")
        pwn.log.info("check_service: update_location OK")

        pwn.log.info(f"Overall duration for check_service: {int(time.time() - start)}s")
        return checkerlib.CheckResult.OK

    def check_flag(self, tick):
        flag = checkerlib.get_flag(tick)
        key = self._get_key(flag)

        pwn.log.info(f"Checking flag {flag} at location {key}")

        stored_val = self._view_treasure(key)

        if not stored_val:
            pwn.log.info("check_flag: view_treasure failed")
            return checkerlib.CheckResult.FLAG_NOT_FOUND
        if stored_val.decode() != flag:
            pwn.log.info("check_service: wrong flag")
            return checkerlib.CheckResult.FLAG_NOT_FOUND

        return checkerlib.CheckResult.OK


if __name__ == '__main__':
    checkerlib.run_check(TreasuryChecker)
