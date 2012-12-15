#!/bin/sh

# exit if any statement returns non-true return value
set -e

# exit on uninitialized variable
set -u

SAMPLES_DIR=pyhwp-tests/hwp5_tests/fixtures
SAMPLE=$SAMPLES_DIR/sample-5017.hwp

hwp5proc | head -n 1 | grep 'Do various'
hwp5proc --help | head -n 1 | grep 'Do various'
hwp5proc --help-commands | grep 'Available <command> values'
hwp5proc --version | grep 'Copyright' | grep 'mete0r'
hwp5proc --version | grep 'License' | grep 'GNU Affero GPL version 3 or any later'
hwp5proc --version | grep 'HWP Binary Specification 1.1' | grep 'Hancom Inc.'

hwp5proc version 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc version --help | head -n 1 | grep 'Print HWP file format version'
hwp5proc version $SAMPLE | grep '5\.0\.1\.7'

hwp5proc header 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc header --help | head -n 1 | grep 'Print HWP file header'
hwp5proc header $SAMPLE | grep 'HWP Document File'

hwp5proc summaryinfo 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc summaryinfo --help | head -n 1 | grep 'Print summary'
hwp5proc summaryinfo $SAMPLE | grep 'clsid: 9fa2'

hwp5proc ls 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc ls --help | head -n 1 | grep 'List streams'
hwp5proc ls $SAMPLE | grep 'PrvText'
hwp5proc ls --vstreams $SAMPLE | grep 'PrvText.utf8'

hwp5proc cat 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc cat --help | head -n 1 | grep 'Extract out the specified stream'
hwp5proc cat $SAMPLE BinData/BIN0002.jpg | file - | grep 'JPEG image data'
hwp5proc cat --vstreams $SAMPLE FileHeader.txt | grep 'HWP Document File'

hwp5proc unpack 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc unpack --help | head -n 1 | grep 'Extract out streams'
rm -rf sample-5017 || echo
hwp5proc unpack $SAMPLE
ls sample-5017 | grep 'FileHeader'
hwp5proc unpack --vstreams $SAMPLE
ls sample-5017 | grep 'FileHeader.txt'
rm -rf sample-5017 || echo

hwp5proc records --help | head -n 1 | grep 'Print the record structure'
hwp5proc records $SAMPLE DocInfo | grep '"seqno": 66,'
hwp5proc records --simple $SAMPLE DocInfo --range=0-2 | grep '0001  HWPTAG_ID_MAPPINGS'
hwp5proc records --simple $SAMPLE DocInfo --range=0-2 | wc -l | grep '^2$'
hwp5proc records --raw $SAMPLE DocInfo --range=0-2 | hwp5proc records --simple | grep '0001  HWPTAG_ID_MAPPINGS'

hwp5proc models 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc models --help | head -n 1 | grep 'Print parsed binary models'
hwp5proc models $SAMPLE DocInfo | grep '"Memo"'
hwp5proc models $SAMPLE docinfo | grep '"Memo"'
hwp5proc models $SAMPLE BodyText/Section0 | grep 'ShapePicture'
hwp5proc models $SAMPLE bodytext/0 | grep 'ShapePicture'
hwp5proc models --simple $SAMPLE bodytext/0 | grep '^0127 '
hwp5proc models --treegroup=1 --simple $SAMPLE bodytext/0 | wc -l | grep '^3$'
hwp5proc cat $SAMPLE BodyText/Section0 | hwp5proc models --simple -V 5.0.1.7 | grep '0127 *ShapePicture'

hwp5proc find 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc find --help | head -n 1 | grep 'Find record models'
hwp5proc find --model=Paragraph $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^14$'
hwp5proc find --tag=HWPTAG_PARA_HEADER $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^14$'
hwp5proc find --tag=66 $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^14$'
hwp5proc find --incomplete $SAMPLE | grep 'Numbering'
hwp5proc find --incomplete --dump $SAMPLE | grep 'STARTEVENT: Numbering'

hwp5proc xml 2>&1 | head -n 1 | grep 'Usage:'
hwp5proc xml --help | head -n 1 | grep 'Transform'
hwp5proc xml $SAMPLE | xmllint --format - | grep 'BinDataEmbedding' | grep 'inline' | wc -l | grep '^0$'
hwp5proc xml --embedbin $SAMPLE | xmllint --format - | grep 'BinDataEmbedding' | grep 'inline' | wc -l | grep '^2$'

hwp5odt 2>&1 | head -n 1 | grep 'Usage:'
hwp5odt --help | head -n 1 | grep 'HWPv5 to ODT converter'
hwp5odt $SAMPLE
unzip -l sample-5017.odt | grep 'styles.xml'
unzip -l sample-5017.odt | grep 'content.xml'
unzip -l sample-5017.odt | grep 'BIN0002.jpg'
unzip -p sample-5017.odt content.xml | xmllint --format - | grep 'office:binary-data' | wc -l | head -n 1 | grep '^0$'
hwp5odt --embed-image $SAMPLE
unzip -p sample-5017.odt content.xml | xmllint --format - | grep 'office:binary-data' | wc -l | head -n 1 | grep '^2$'
rm -f sample-5017.odt
