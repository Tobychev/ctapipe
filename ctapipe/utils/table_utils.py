import astropy.table as tab
import astropy.table.column as astrocol

from ctapipe.io import TableLoader


def explain_astrotable(table):
    """Simple helper function that displays the columns in a astropy.table"""
    for itm in table.itercols():
        if isinstance(itm, astrocol.Column):
            print(f"{itm.name:<35} {itm.description:<40} {str(itm.unit):>6}")


def get_cameras_in_file(infile):
    """
    Simple function that inspect the meta instrument table and returns the telescope numbers and camera types present in a file
    """
    meta = TableLoader(
        infile,
        load_instrument=True,
        load_simulated=False,
        load_dl1_images=False,
        load_true_images=False,
    )
    camera_kinds = tab.unique(
        meta.instrument_table["camera_name", "tel_id"], keys=["camera_name"]
    )["camera_name"].data
    tels_here = dict()
    for cam in camera_kinds:
        sel = meta.instrument_table["camera_name"] == cam
        tels_here[cam] = tab.unique(
            meta.instrument_table["tel_id", "name"][sel], keys=["tel_id"]
        )["tel_id"].data
    return tels_here, camera_kinds
