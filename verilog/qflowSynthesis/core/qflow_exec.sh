#!/usr/bin/tcsh -f
#-------------------------------------------
# qflow exec script for project /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core
#-------------------------------------------

# /usr/lib/qflow/scripts/synthesize.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
# /usr/lib/qflow/scripts/placement.sh -d /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
/usr/lib/qflow/scripts/vesta.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
# /usr/lib/qflow/scripts/router.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
# /usr/lib/qflow/scripts/placement.sh -f -d /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
# /usr/lib/qflow/scripts/router.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1 $status
# /usr/lib/qflow/scripts/cleanup.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
# /usr/lib/qflow/scripts/display.sh /home/jose/Documents/gitRepos/scratchComputer/verilog/qflowSynthesis/core core || exit 1
