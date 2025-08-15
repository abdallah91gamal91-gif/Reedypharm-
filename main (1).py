
# EL REEDY PHARMACY - Kivy App (EN/AR + Light/Dark)
import csv, os, datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

CSV_FILE = "medicines.csv"
LOGO_FILE = "logo.png"

class ReedyApp(App):
    def build(self):
        self.lang = "en"
        self.dark = False
        self.strings = {
            "en": {"title":"EL REEDY PHARMACY","search_hint":"Search by name/strength/form...","medicines":"Medicines","cart":"Cart","reload":"Reload CSV","add_item":"Add Item","manage_db":"Manage DB","qty":"Quantity","add":"Add","cancel":"Cancel","discount":"Discount (EGP)","save_receipt":"Save Receipt","clear_cart":"Clear Cart","enter_qty":"Enter quantity","invalid_qty":"Invalid quantity","info":"Info","error":"Error","saved":"Saved: {} & {}","data_reloaded":"Data reloaded from CSV.","item_added":"Item added to CSV.","name_en":"Name (EN)","name_ar":"Name (AR)","strength":"Strength","form":"Form","price":"Price (EGP)","add_to_db":"Add to DB","delete":"Delete","close":"Close","total":"Total: EGP {:.2f}","empty_cart":"Cart is empty"},
            "ar": {"title":"صيدلية الريدي","search_hint":"ابحث بالاسم/التركيز/الهيئة...","medicines":"الأدوية","cart":"السلة","reload":"تحديث البيانات","add_item":"إضافة صنف","manage_db":"إدارة القاعدة","qty":"الكمية","add":"إضافة","cancel":"إلغاء","discount":"خصم (جنيه)","save_receipt":"حفظ إيصال","clear_cart":"تفريغ السلة","enter_qty":"أدخل الكمية","invalid_qty":"كمية غير صالحة","info":"معلومة","error":"خطأ","saved":"تم الحفظ: {} و {}","data_reloaded":"تم تحديث البيانات من CSV.","item_added":"تمت إضافة الصنف.","name_en":"الاسم (إنجليزي)","name_ar":"الاسم (عربي)","strength":"التركيز","form":"الهيئة الدوائية","price":"السعر (جنيه)","add_to_db":"حفظ","delete":"حذف","close":"إغلاق","total":"الإجمالي: {:.2f} جنيه","empty_cart":"السلة فارغة"}
        }
        self._set_theme(self.dark)
        self.items = self._read_csv()
        self.filtered = list(self.items)
        self.cart = []
        self.discount = 0.0

        root = BoxLayout(orientation="vertical", padding=dp(6), spacing=dp(6))

        header = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(6))
        with header.canvas.before:
            Color(*self.COL_HEADER)
            self._hdr_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *_: setattr(self._hdr_rect, "pos", header.pos),
                    size=lambda *_: setattr(self._hdr_rect, "size", header.size))

        if os.path.exists(LOGO_FILE):
            header.add_widget(Image(source=LOGO_FILE, allow_stretch=True, keep_ratio=True, size_hint_x=0.2))
        else:
            header.add_widget(Label(text="💊", color=self.C_TEXT, size_hint_x=0.18, font_size=dp(32)))

        self.title_lbl = Label(text=self.t("title"), color=self.C_TEXT, bold=True)
        header.add_widget(self.title_lbl)

        lang_btn = Button(text="EN/AR", size_hint_x=None, width=dp(80),
                          background_color=self.COL_ACCENT, color=self.C_TEXT_BTN)
        theme_btn = Button(text="☀/🌙", size_hint_x=None, width=dp(80),
                           background_color=self.COL_ACCENT, color=self.C_TEXT_BTN)
        lang_btn.bind(on_release=lambda *_: self.toggle_lang())
        theme_btn.bind(on_release=lambda *_: self.toggle_theme())
        header.add_widget(lang_btn); header.add_widget(theme_btn)
        root.add_widget(header)

        tools = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        self.search = TextInput(hint_text=self.t("search_hint"), multiline=False,
                                background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG)
        btn_reload = Button(text=self.t("reload"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(120))
        btn_add = Button(text=self.t("add_item"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(110))
        btn_settings = Button(text=self.t("manage_db"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(120))
        tools.add_widget(self.search); tools.add_widget(btn_reload); tools.add_widget(btn_add); tools.add_widget(btn_settings)
        self.search.bind(text=lambda *_: self.apply_filter())
        btn_reload.bind(on_release=lambda *_: self.reload_data())
        btn_add.bind(on_release=lambda *_: self.open_add_popup())
        btn_settings.bind(on_release=lambda *_: self.open_manage_popup())
        root.add_widget(tools)

        body = GridLayout(cols=2, spacing=dp(6))
        left = BoxLayout(orientation="vertical")
        left.add_widget(Label(text="[b]{}[/b]".format(self.t("medicines")), markup=True, color=self.C_TEXT, size_hint_y=None, height=dp(26)))
        self.items_scroll = ScrollView()
        self.items_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=dp(4))
        self.items_container.bind(minimum_height=self.items_container.setter("height"))
        self.items_scroll.add_widget(self.items_container)
        left.add_widget(self.items_scroll)
        body.add_widget(left)

        right = BoxLayout(orientation="vertical")
        right.add_widget(Label(text="[b]{}[/b]".format(self.t("cart")), markup=True, color=self.C_TEXT, size_hint_y=None, height=dp(26)))
        self.cart_scroll = ScrollView()
        self.cart_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), padding=dp(4))
        self.cart_container.bind(minimum_height=self.cart_container.setter("height"))
        self.cart_scroll.add_widget(self.cart_container)
        right.add_widget(self.cart_scroll)

        totals = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        self.disc_input = TextInput(hint_text=self.t("discount"), multiline=False, input_filter="float",
                                    background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG)
        btn_save = Button(text=self.t("save_receipt"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(130))
        btn_clear = Button(text=self.t("clear_cart"), background_color=self.COL_DIM, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(110))
        totals.add_widget(self.disc_input); totals.add_widget(btn_save); totals.add_widget(btn_clear)
        right.add_widget(totals)

        self.total_lbl = Label(text=self.t("total").format(0.0), color=self.C_TEXT, size_hint_y=None, height=dp(28))
        right.add_widget(self.total_lbl)
        body.add_widget(right); root.add_widget(body)

        self.refresh_items()
        btn_save.bind(on_release=lambda *_: self.save_receipt())
        btn_clear.bind(on_release=lambda *_: self.clear_cart())
        return root

    def t(self, key): return self.strings[self.lang].get(key, key)

    def _set_theme(self, dark):
        if dark:
            Window.clearcolor = (0.08, 0.08, 0.10, 1)
            self.COL_HEADER = (0.75, 0.15, 0.15, 1)
            self.COL_PRIMARY = (0.85, 0.20, 0.20, 1)
            self.COL_ACCENT = (0.25, 0.25, 0.28, 1)
            self.COL_DIM = (0.35, 0.35, 0.38, 1)
            self.C_TEXT = (1, 1, 1, 1); self.C_TEXT_BTN = (1, 1, 1, 1)
            self.C_INPUT_BG = (0.18, 0.18, 0.2, 1); self.C_INPUT_FG = (1, 1, 1, 1)
        else:
            Window.clearcolor = (1, 1, 1, 1)
            self.COL_HEADER = (0.83, 0.18, 0.18, 1)
            self.COL_PRIMARY = (0.9, 0.2, 0.2, 1)
            self.COL_ACCENT = (0.95, 0.95, 0.95, 1)
            self.COL_DIM = (0.7, 0.7, 0.7)
            self.C_TEXT = (0, 0, 0, 1); self.C_TEXT_BTN = (1, 1, 1, 1)
            self.C_INPUT_BG = (1, 1, 1, 1); self.C_INPUT_FG = (0, 0, 0, 1)

    def toggle_theme(self): self.dark = not self.dark; self._set_theme(self.dark); self.stop(); ReedyApp().run()
    def toggle_lang(self):  self.lang = "ar" if self.lang == "en" else "en"; self.stop(); app = ReedyApp(); app.lang = self.lang; app.dark = self.dark; app.run()

    def _read_csv(self):
        items = []
        if not os.path.exists(CSV_FILE): return items
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                try: price = float(str(row.get("price_egp", "0")).strip())
                except: price = 0.0
                items.append({"name_en":row.get("name_en","").strip(),"name_ar":row.get("name_ar","").strip(),"strength":row.get("strength","").strip(),"form":row.get("form","").strip(),"price":price})
        return items

    def _write_csv(self, items):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["name_en","name_ar","strength","form","price_egp"])
            for it in items: w.writerow([it["name_en"], it["name_ar"], it["strength"], it["form"], f"{it['price']:.2f}"])

    def refresh_items(self):
        self.items_container.clear_widgets()
        for it in self.filtered: self.items_container.add_widget(self._item_row(it))

    def _item_row(self, it):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(6))
        txt_name = it["name_ar"] if self.lang == "ar" and it["name_ar"] else it["name_en"]
        lbl = Label(text=f"{txt_name} | {it['strength']} | {it['form']}  —  EGP {it['price']:.2f}", color=self.C_TEXT, halign="left", valign="middle")
        lbl.bind(size=lambda *_: setattr(lbl, 'text_size', lbl.size))
        btn = Button(text=self.t("add"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN, size_hint_x=None, width=dp(100))
        btn.bind(on_release=lambda *_: self.add_to_cart(it))
        row.add_widget(lbl); row.add_widget(btn); return row

    def apply_filter(self):
        q = (self.search.text or "").strip().lower()
        if not q: self.filtered = list(self.items)
        else:
            def match(it): return q in f"{it['name_en']} {it['name_ar']} {it['strength']} {it['form']}".lower()
            self.filtered = [i for i in self.items if match(i)]
        self.refresh_items()

    def reload_data(self): self.items = self._read_csv(); self.apply_filter(); self._toast(self.t("info"), self.t("data_reloaded"))

    def add_to_cart(self, item):
        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))
        ti = TextInput(hint_text=self.t("qty"), multiline=False, input_filter="int",background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG)
        btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        ok = Button(text=self.t("add"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN)
        cancel = Button(text=self.t("cancel"), background_color=self.COL_DIM, color=self.C_TEXT_BTN)
        btns.add_widget(ok); btns.add_widget(cancel)
        content.add_widget(Label(text=self.t("enter_qty"), color=self.C_TEXT)); content.add_widget(ti); content.add_widget(btns)
        pop = Popup(title=self.t("qty"), content=content, size_hint=(0.85, 0.4))
        cancel.bind(on_release=pop.dismiss)
        def _do_add(*_):
            try: qty = int(ti.text); assert qty>0
            except: self._toast(self.t("error"), self.t("invalid_qty")); return
            entry = {**item, "qty": qty, "subtotal": item["price"] * qty}
            if not hasattr(self,"cart"): self.cart = []
            self.cart.append(entry); self.refresh_cart(); pop.dismiss()
        ok.bind(on_release=_do_add); pop.open()

    def refresh_cart(self):
        self.cart_container.clear_widgets()
        if not hasattr(self,"cart"): self.cart = []
        for e in self.cart: self.cart_container.add_widget(self._cart_row(e))
        self.recalc()

    def _cart_row(self, e):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
        txt_name = e["name_ar"] if self.lang == "ar" and e["name_ar"] else e["name_en"]
        lbl = Label(text=f"{txt_name} ({e['strength']}) x{e['qty']}", color=self.C_TEXT, halign="left", valign="middle")
        lbl.bind(size=lambda *_: setattr(lbl, 'text_size', lbl.size))
        sub = Label(text=f"EGP {e['subtotal']:.2f}", color=self.C_TEXT, size_hint_x=None, width=dp(110))
        btn = Button(text="✕", size_hint_x=None, width=dp(40), background_color=self.COL_DIM, color=self.C_TEXT_BTN)
        btn.bind(on_release=lambda *_: self._remove_from_cart(e))
        row.add_widget(lbl); row.add_widget(sub); row.add_widget(btn); return row

    def _remove_from_cart(self, e): self.cart.remove(e); self.refresh_cart()
    def clear_cart(self): self.cart = []; self.refresh_cart()

    def recalc(self):
        try: self.discount = float(self.disc_input.text or 0)
        except: self.discount = 0.0
        total = sum(e["subtotal"] for e in self.cart) - self.discount
        if total < 0: total = 0.0
        self.total_lbl.text = self.t("total").format(total)

    def save_receipt(self):
        if not self.cart: self._toast(self.t("error"), self.t("empty_cart")); return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        txt = f"receipt_{ts}.txt"; csvf = f"receipt_{ts}.csv"
        total = sum(e["subtotal"] for e in self.cart); final = max(0.0, total - self.discount)
        with open(txt, "w", encoding="utf-8") as f:
            title = "EL REEDY PHARMACY" if self.lang=="en" else "صيدلية الريدي"
            f.write(title + " - Receipt\n" + "="*36 + "\n")
            for e in self.cart:
                name = e["name_ar"] if self.lang=="ar" and e["name_ar"] else e["name_en"]
                f.write(f"{name} {e['strength']} x{e['qty']} - EGP {e['subtotal']:.2f}\n")
            f.write("-"*36 + "\n"); f.write(f"Subtotal: EGP {total:.2f}\n")
            f.write(f"Discount: EGP {self.discount:.2f}\n"); f.write(f"TOTAL:    EGP {final:.2f}\n")
        with open(csvf, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["name","strength","qty","unit_price","subtotal"])
            for e in self.cart:
                w.writerow([e["name_en"], e["strength"], e["qty"], f"{e['price']:.2f}", f"{e['subtotal']:.2f}"])
            w.writerow([]); w.writerow(["Subtotal", f"{total:.2f}"]); w.writerow(["Discount", f"{self.discount:.2f}"]); w.writerow(["TOTAL", f"{final:.2f}"])
        self._toast(self.t("info"), self.t("saved").format(txt, csvf))

    def open_add_popup(self):
        content = GridLayout(cols=2, spacing=dp(6), padding=dp(6))
        content.add_widget(Label(text=self.t("name_en"), color=self.C_TEXT)); name_en = TextInput(multiline=False, background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG); content.add_widget(name_en)
        content.add_widget(Label(text=self.t("name_ar"), color=self.C_TEXT)); name_ar = TextInput(multiline=False, background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG); content.add_widget(name_ar)
        content.add_widget(Label(text=self.t("strength"), color=self.C_TEXT)); st = TextInput(multiline=False, background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG); content.add_widget(st)
        content.add_widget(Label(text=self.t("form"), color=self.C_TEXT)); form = TextInput(multiline=False, background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG); content.add_widget(form)
        content.add_widget(Label(text=self.t("price"), color=self.C_TEXT)); price = TextInput(multiline=False, input_filter="float", background_color=self.C_INPUT_BG, foreground_color=self.C_INPUT_FG); content.add_widget(price)
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        ok = Button(text=self.t("add_to_db"), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN)
        cancel = Button(text=self.t("cancel"), background_color=self.COL_DIM, color=self.C_TEXT_BTN)
        box = BoxLayout(orientation="vertical"); box.add_widget(content); btns.add_widget(ok); btns.add_widget(cancel); box.add_widget(btns)
        pop = Popup(title=self.t("add_item"), content=box, size_hint=(0.9, 0.7))
        cancel.bind(on_release=pop.dismiss)
        def _save(*_):
            try: p = float(price.text); assert name_en.text.strip()
            except: self._toast(self.t("error"), self.t("invalid_qty")); return
            new_item = {"name_en":name_en.text.strip(), "name_ar":name_ar.text.strip(), "strength":st.text.strip(), "form":form.text.strip(), "price":p}
            self.items.append(new_item); self._write_csv(self.items); self.reload_data(); pop.dismiss(); self._toast(self.t("info"), self.t("item_added"))
        ok.bind(on_release=_save); pop.open()

    def open_manage_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))
        sc = ScrollView(size_hint=(1,1))
        cont = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        cont.bind(minimum_height=cont.setter("height"))
        for idx, it in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
            nm = it["name_ar"] if self.lang=="ar" and it["name_ar"] else it["name_en"]
            lbl = Label(text=f"{nm} | {it['strength']} | {it['form']} | EGP {it['price']:.2f}", color=self.C_TEXT, halign="left", valign="middle")
            lbl.bind(size=lambda *_: setattr(lbl, 'text_size', lbl.size))
            del_btn = Button(text=self.t("delete"), size_hint_x=None, width=dp(90), background_color=self.COL_DIM, color=self.C_TEXT_BTN)
            def make_del(i): return lambda *_: self._delete_item(i, pop)
            del_btn.bind(on_release=make_del(idx))
            row.add_widget(lbl); row.add_widget(del_btn); cont.add_widget(row)
        sc.add_widget(cont); content.add_widget(sc)
        close_btn = Button(text=self.t("close"), size_hint_y=None, height=dp(44), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN)
        content.add_widget(close_btn)
        pop = Popup(title=self.t("manage_db"), content=content, size_hint=(0.95, 0.85))
        close_btn.bind(on_release=pop.dismiss); pop.open()

    def _delete_item(self, index, parent_pop):
        if 0 <= index < len(self.items):
            del self.items[index]; self._write_csv(self.items); self.reload_data(); parent_pop.dismiss(); self.open_manage_popup()

    def _toast(self, title, msg):
        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))
        content.add_widget(Label(text=msg, color=self.C_TEXT))
        btn = Button(text=self.t("close"), size_hint_y=None, height=dp(40), background_color=self.COL_PRIMARY, color=self.C_TEXT_BTN)
        content.add_widget(btn)
        pop = Popup(title=title, content=content, size_hint=(0.85, 0.35))
        btn.bind(on_release=pop.dismiss); pop.open()

if __name__ == "__main__":
    ReedyApp().run()
