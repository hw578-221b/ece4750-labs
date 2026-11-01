#========================================================================= 
# test_harness
#=========================================================================

import struct
from pymtl3 import *
from pymtl3.datatypes import mk_bits
from pymtl3.stdlib.mem import MemoryFL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.test_utils import run_sim
from lab2_proc.tinyrv2_encoding import assemble

#=========================================================================

def asm_test(func):
    name = func.__name__
    if name.startswith("gen_"):
        name = name[4:]
    if name.endswith("_test"):
        name = name[:-5]
    return (name, func)

#=========================================================================

class SingleCoreTestHarness(Component):

    def construct(s, Sys, commit_width=1):
        # Configurable commit_inst width
        s.commit_inst = OutPort(mk_bits(commit_width))

        s.src  = StreamSourceFL(Bits32, [])
        s.sink = StreamSinkFL(Bits32, [])
        s.sys  = Sys()
        s.mem  = MemoryFL(2, mem_ifc_dtypes=[mk_mem_msg(8,32,128), mk_mem_msg(8,32,128)])

        s.sys.commit_inst //= s.commit_inst

        # System <-> Proc/Mngr
        s.src.ostream   //= s.sys.mngr2proc
        s.sys.proc2mngr //= s.sink.istream

        # System <-> Memory
        s.sys.imem //= s.mem.ifc[0]
        s.sys.dmem //= s.mem.ifc[1]

    #-----------------------------
    # load memory sections
    #-----------------------------

    def load(s, mem_image):
        sections = mem_image.get_sections()
        for section in sections:
            if section.name == ".mngr2proc":
                for bits in struct.iter_unpack("<I", section.data):
                    s.src.msgs.append(b32(bits[0]))
            elif section.name == ".proc2mngr":
                for bits in struct.iter_unpack("<I", section.data):
                    s.sink.msgs.append(b32(bits[0]))
            else:
                start_addr = section.addr
                stop_addr  = section.addr + len(section.data)
                s.mem.mem.mem[start_addr:stop_addr] = section.data

    def cleanup(s):
        del s.mem.mem[:]

    def done(s):
        return s.src.done() and s.sink.done()

    def line_trace(s):
        imem_reqstr = "  "
        if s.mem.ifc[0].reqstream.val and s.mem.ifc[0].reqstream.rdy:
            imem_reqstr = MemMsgType.str[int(s.mem.ifc[0].reqstream.msg.type_)]
        imem_respstr = "  "
        if s.mem.ifc[0].respstream.val and s.mem.ifc[0].respstream.rdy:
            imem_respstr = MemMsgType.str[int(s.mem.ifc[0].respstream.msg.type_)]
        imem_str = "     " if imem_reqstr=="  " and imem_respstr=="  " else f"{imem_reqstr}>{imem_respstr}"

        dmem_reqstr = "  "
        if s.mem.ifc[1].reqstream.val and s.mem.ifc[1].reqstream.rdy:
            dmem_reqstr = MemMsgType.str[int(s.mem.ifc[1].reqstream.msg.type_)]
        dmem_respstr = "  "
        if s.mem.ifc[1].respstream.val and s.mem.ifc[1].respstream.rdy:
            dmem_respstr = MemMsgType.str[int(s.mem.ifc[1].respstream.msg.type_)]
        dmem_str = "     " if dmem_reqstr=="  " and dmem_respstr=="  " else f"{dmem_reqstr}>{dmem_respstr}"

        mem_str = f"{imem_str}|{dmem_str}"
        return s.src.line_trace() + " >" + ("*" if s.sys.stats_en else " ") + s.sys.line_trace() + " " + mem_str + " > " + s.sink.line_trace()

#=========================================================================

def run_score_test(Sys, gen_test, delays=False, cmdline_opts=None, commit_width=1):
    th = SingleCoreTestHarness(Sys, commit_width=commit_width)

    if delays:
        th.set_param("top.src.construct", initial_delay=0, interval_delay=20, interval_delay_mode='random')
        th.set_param("top.sink.construct", initial_delay=0, interval_delay=20, interval_delay_mode='random')
        th.set_param("top.mem.construct", stall_prob=0.5, extra_latency=3)

    th.elaborate()

    asm_prog = gen_test if isinstance(gen_test, str) else gen_test()
    mem_image = assemble(asm_prog)
    th.load(mem_image)
    run_sim(th, cmdline_opts, duts=['sys'])

#=========================================================================

class MultiCoreTestHarness(Component):

    def construct(s, Sys, num_cores=4, commit_width=1):
        # Configurable commit_inst width and number of cores
        s.commit_inst = OutPort(mk_bits(commit_width))
        s.srcs  = [ StreamSourceFL(Bits32, []) for _ in range(num_cores) ]
        s.sinks = [ StreamSinkFL(Bits32, [])   for _ in range(num_cores) ]
        s.sys   = Sys()
        s.mem   = MemoryFL(2, mem_ifc_dtypes=[mk_mem_msg(8,32,128), mk_mem_msg(8,32,128)])

        s.sys.commit_inst //= s.commit_inst

        for i in range(num_cores):
            s.srcs[i].ostream  //= s.sys.mngr2proc[i]
            s.sys.proc2mngr[i] //= s.sinks[i].istream

        s.sys.imem //= s.mem.ifc[0]
        s.sys.dmem //= s.mem.ifc[1]

    def load(s, mem_image):
        sections = mem_image.get_sections()
        for section in sections:
            if section.name == ".mngr2proc":
                for i in range(len(s.srcs)):
                    for bits in struct.iter_unpack("<I", section.data):
                        s.srcs[i].msgs.append(b32(bits[0]))
            elif section.name.startswith(".mngr2proc_"):
                idx = int(section.name.split("_")[1])
                for bits in struct.iter_unpack("<I", section.data):
                    s.srcs[idx].msgs.append(b32(bits[0]))
            elif section.name == ".proc2mngr":
                for i in range(len(s.sinks)):
                    for bits in struct.iter_unpack("<I", section.data):
                        s.sinks[i].msgs.append(b32(bits[0]))
            elif section.name.startswith(".proc2mngr_"):
                idx = int(section.name.split("_")[1])
                for bits in struct.iter_unpack("<I", section.data):
                    s.sinks[idx].msgs.append(b32(bits[0]))
            else:
                start_addr = section.addr
                stop_addr  = section.addr + len(section.data)
                s.mem.mem.mem[start_addr:stop_addr] = section.data

    def cleanup(s):
        del s.mem.mem[:]

    def done(s):
        return all(src.done() and sink.done() for src, sink in zip(s.srcs, s.sinks))

    def line_trace(s):
        imem_reqstr = "  "
        if s.mem.ifc[0].reqstream.val and s.mem.ifc[0].reqstream.rdy:
            imem_reqstr = MemMsgType.str[int(s.mem.ifc[0].reqstream.msg.type_)]
        imem_respstr = "  "
        if s.mem.ifc[0].respstream.val and s.mem.ifc[0].respstream.rdy:
            imem_respstr = MemMsgType.str[int(s.mem.ifc[0].respstream.msg.type_)]
        imem_str = "     " if imem_reqstr=="  " and imem_respstr=="  " else f"{imem_reqstr}>{imem_respstr}"

        dmem_reqstr = "  "
        if s.mem.ifc[1].reqstream.val and s.mem.ifc[1].reqstream.rdy:
            dmem_reqstr = MemMsgType.str[int(s.mem.ifc[1].reqstream.msg.type_)]
        dmem_respstr = "  "
        if s.mem.ifc[1].respstream.val and s.mem.ifc[1].respstream.rdy:
            dmem_respstr = MemMsgType.str[int(s.mem.ifc[1].respstream.msg.type_)]
        dmem_str = "     " if dmem_reqstr=="  " and dmem_respstr=="  " else f"{dmem_reqstr}>{dmem_respstr}"

        mem_str = f"{imem_str}|{dmem_str}"
        srcs_str  = "|".join([ src.line_trace()  for src  in s.srcs  ])
        sinks_str = "|".join([ sink.line_trace() for sink in s.sinks ])
        return srcs_str + " >" + ("*" if s.sys.stats_en else " ") + s.sys.line_trace() + " " + mem_str + " > " + sinks_str

#=========================================================================

def run_mcore_test(Sys, gen_test, delays=False, cmdline_opts=None, num_cores=4, commit_width=1):
    th = MultiCoreTestHarness(Sys, num_cores=num_cores, commit_width=commit_width)

    if delays:
        th.set_param("top.src.construct", initial_delay=0, interval_delay=20, interval_delay_mode='random')
        th.set_param("top.sink.construct", initial_delay=0, interval_delay=20, interval_delay_mode='random')
        th.set_param("top.mem.construct", stall_prob=0.5, extra_latency=3)

    th.elaborate()

    asm_prog = gen_test if isinstance(gen_test, str) else gen_test()
    mem_image = assemble(asm_prog)
    th.load(mem_image)
    run_sim(th, cmdline_opts, duts=['sys'])
