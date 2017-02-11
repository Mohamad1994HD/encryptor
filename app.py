import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from enc import Operation, EncEngine

class Application(Gtk.Window):
    class Filter(object):
        def __init__(self, type, desc):
            self.type = type
            self.description = desc

        def General(cls):
            return MainWindow.Filter('*', 'Any file')
        General = classmethod(General)

    operation = Operation.ENCRYPT
    ftype_slection = Operation.FILE_SELECT

    FileDialogConsts = {'file_open':Gtk.STOCK_OPEN,
                        'file_open_action': Gtk.FileChooserAction.OPEN,
                        'file_save_action': Gtk.FileChooserAction.SAVE,
                        'folder_select': 'Select',
                        'folder_select_action': Gtk.FileChooserAction.SELECT_FOLDER}


    def __init__(self):
        self.engine = EncEngine()

        Gtk.Window.__init__(self, title='Encryptor 0.1')
        hbox = Gtk.Box(spacing=10)
        self.add(hbox)

        vbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        hbox.add(vbox)

        chose_box = Gtk.Box(spacing=6)

        # Choose Encryption / Decryption Btns
        op_box = Gtk.Box(spacing=15, orientation=Gtk.Orientation.VERTICAL)
        op_frame = Gtk.Frame(label='Operation')
        op_frame.add(op_box)

        encrpt_slct = Gtk.RadioButton("Encrypt")
        dcrpt_slct = Gtk.RadioButton("Decrypt")

        encrpt_slct.connect("toggled", self._on_op_selection, Operation.ENCRYPT)
        dcrpt_slct.connect('toggled', self._on_op_selection, Operation.DECRYPT)
        Gtk.RadioButton.join_group(encrpt_slct, dcrpt_slct)
        op_box.add(encrpt_slct)
        op_box.add(dcrpt_slct)

        chose_box.add(op_frame)
        vbox.add(chose_box)

        # Key menu
        key_frame = Gtk.Frame(label='Key')
        key_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        key_frame.add(key_box)
        chose_box.add(key_frame)

        self.key_input = Gtk.Entry()

        select_key_btn = Gtk.Button('Select key file')
        save_key_btn = Gtk.Button('Save key as')
        generate_key_btn = Gtk.Button('Generate new key')

        save_key_btn.connect('clicked', self._on_save_key_clicked)
        select_key_btn.connect('clicked', self._on_select_key_clicked)
        generate_key_btn.connect('clicked', self._on_generate_key_clicked)

        kbtn_bx = Gtk.Box()
        kbtn_bx.add(select_key_btn)
        kbtn_bx.add(generate_key_btn)
        kbtn_bx.add(save_key_btn)
        key_box.add(self.key_input)
        key_box.add(kbtn_bx)

        # File/Folder Selection
        slct_frame = Gtk.Frame(label='File/Folder Selection')

        file_slct = Gtk.RadioButton('File')
        folder_slct = Gtk.RadioButton('Folder')
        file_slct.connect('toggled', self._on_file_op_select, Operation.FILE_SELECT)
        folder_slct.connect('toggled', self._on_file_op_select, Operation.FOLDER_SELECT)

        Gtk.RadioButton.join_group(file_slct, folder_slct)

        slct_btn = Gtk.Button("Select")
        run_btn = Gtk.Button("Do job")


        slct_btn.connect('clicked', self._on_file_select)
        run_btn.connect('clicked', self._on_run)

        self.fpath_entry = Gtk.Entry()
        self.fpath_entry.set_editable(False)

        slct_box = Gtk.Box(spacing=6)
        fselect_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        fselect_box.add(file_slct)
        fselect_box.add(folder_slct)
        slct_box.add(fselect_box)
        slct_box.add(slct_btn)
        slct_box.add(self.fpath_entry)
        slct_frame.add(slct_box)

        vbox.add(slct_frame)
        vbox.add(run_btn)

        # default
        encrpt_slct.set_active(True)
        file_slct.set_active(True)

    def _on_run(self, widget):
        print "run"
        self.engine.run(optype=self.operation)

    def _on_file_select(self, widget):
        print "select your file/folder to encrypt"

        if self.ftype_slection == Operation.FILE_SELECT:
            type = {'optype':self.FileDialogConsts['file_open_action'],
                    'opconst':self.FileDialogConsts['file_open']}
        elif self.ftype_slection == Operation.FOLDER_SELECT:
            type = {'optype':self.FileDialogConsts['folder_select_action'],
                    'opconst':self.FileDialogConsts['folder_select']}

        self.create_file_dialog(type['optype'], type['opconst'],
                                title='Select',
                                callback=self._on_target_file_picked)

    def _on_target_file_picked(self, path):
        # set the encryption destination as path
        # extract paths from folder
        self.engine.target_ = [path]
        # update target entry text
        self.fpath_entry.set_text(path)

    def _on_op_selection(self, widget, op):
        if widget.get_active():
            self.operation = op
            print self.operation

    def _on_file_op_select(self, widget, op):
        if widget.get_active():
            self.ftype_slection = op
            print self.ftype_slection

    def _on_save_key_clicked(self, widget):
        # Save the key file
        save_key = lambda path: self.engine.save_key_as(path)

        self.create_file_dialog(self.FileDialogConsts['file_save_action'],
                                self.FileDialogConsts['file_open'],
                                title='Save key as',
                                callback=save_key)

    def _on_select_key_clicked(self, widget):
        # Select the key file
        print "Select your key file"
        #load_key = lambda path: self.engine.load_key(path)
        self.create_file_dialog(self.FileDialogConsts['file_open_action'],
                                self.FileDialogConsts['file_open'],
                                title='Select encryption key file',
                                callback=self._on_key_load,
                                filters=[Application.Filter("text/plain",'*.txt file')])
    def _on_key_load(self, path):
        self.engine.load_key(path)
        self.key_input.set_text(self.engine.get_key())

    def _on_generate_key_clicked(self, widget):
        print "generate new key"
        # generate a new key randomly
        self.engine.gen_key()
        self.key_input.set_text(self.engine.get_key())

    def add_filters(self, dialog, filters):
        for f in filters:
            filter_ = Gtk.FileFilter()
            filter_.set_name(f.description)
            filter_.add_mime_type(f.type)
            dialog.add_filter(filter_)


    def create_file_dialog(self, optype, opconst, title, callback,
                           filters=None):
        dialog = Gtk.FileChooserDialog(title,
                                       self,
                                       optype,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        opconst,
                                        Gtk.ResponseType.OK))
        if filters:
            self.add_filters(dialog, filters=filters)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print "file: {0}".format(dialog.get_filename())
            callback(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print "Canceled"

        dialog.destroy()

if __name__ == '__main__':
    win = Application()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
