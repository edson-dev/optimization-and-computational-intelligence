from pgmpy.readwrite import BIFReader, XMLBIFWriter
if __name__ == "__main__":

    # Load the BIF file
    reader = BIFReader("bif/asia.bif")
    model = reader.get_model()

    # Write the model to XMLBIF format
    XMLBIFWriter(model).write_xmlbif("bif/asia.xmlbif")
