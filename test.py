from Common.Process import *

from Test import db_access
from Test import entry
from Test import db_view
from Test import infowidget

if __name__ == "__main__":
    pm = ProcessManager()
    pm.StartWorkers()

    # db_access.test_db()
    # entry.main()
    # db_view.main()
    infowidget.main()
