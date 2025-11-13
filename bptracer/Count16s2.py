class Count16sRunner(BaseRunner):
    def build_command(self):
        cmd = textwrap.dedent(rf"""
        cd {config.OUTPUT_PATH}
        mkdir {id}
        cd {id}
        {config.bwa}  mem -d {config.SARG_DATABASE} -q {file1} \
            -o {id}.m8  \
            -t ./ \
            -b 8 \
            -f {config.SARG_FORMAT} \
            --evalue {config.SARG_EVALUE} \
            -t {config.SARG_MAX_TARGET_SEQS} \


             """)
        return cmd
# 这种做法就是self和file里面都是
def count_16s(self, file):
    '''
    Count 16S (GreenGenes 16S rRNA Database 85%) copy number using bwa (pre-filtering) and blastn (post-filtering).
    '''
    ## pre-filtering using bwa
    subprocess.run([
        'bwa', 'mem',
        '-t', str(self.thread),
        '-o', file.tmp_16s_sam,
        self.setting.gg85, file.file], check=True, stderr=subprocess.DEVNULL)

    ## convert sam to fasta for later usage, note that reads can be duplicated
    with open(file.tmp_16s_fa, 'w') as f:
        subprocess.run([
            'samtools',
            'fasta',
            '-F', '2308',
            file.tmp_16s_sam], check=True, stderr=subprocess.DEVNULL, stdout=f)

    ## post-filter using blastn
    ## switch mt_mode if too little queries or too many threads, blast raises error if <2,500,000 bases per thread
    mt_mode = '1' if simple_count(file.tmp_16s_fa)[0] / self.thread >= 2500000 else '0'
    subprocess.run([
        'blastn',
        '-db', self.setting.gg85,
        '-query', file.tmp_16s_fa,
        '-out', file.tmp_16s_txt,
        '-outfmt', ' '.join(['6'] + self.setting.columns),
        '-evalue', str(self.e1),
        '-max_hsps', '1',
        '-max_target_seqs', '1',
        '-mt_mode', mt_mode,
        '-num_threads', str(self.thread)], check=True, stderr=subprocess.DEVNULL)

    ## process blastn results, store subject cover
    df = pd.read_table(file.tmp_16s_txt, header=None, names=self.setting.columns)
    if len(df) == 0:
        logger.warning(f'No 16S-like sequences found in file <{file.file}>.')
    else:
        if df['qseqid'].duplicated().sum() > 0:
            logger.warning('Duplicated sequences in 16S copy number calculation.')
            df = df[~df['qseqid'].duplicated()]

        return (df['length'] / df['slen']).sum()




def count_cells(self, file):
    '''
    Count Essential Single Copy Marker Genes (cell number) using diamond.
    '''
    ## filter using diamond
    subprocess.run([
                       'diamond', 'blastx',
                       '--db', f'{self.setting.ko30}.dmnd',
                       '--query', file.file,
                       '--out', file.tmp_cells_txt,
                       '--outfmt', '6'] + self.setting.columns + [
                       '--evalue', str(self.e2),
                       '--id', str(self.id),
                       '--query-cover', str(self.qcov),
                       '--max-hsps', '1',
                       '--max-target-seqs', '1',
                       '--threads', str(self.thread),
                       '--quiet'], check=True, stderr=subprocess.DEVNULL)

    ## process blastx results, store subject coverage
    df = pd.merge(pd.read_table(file.tmp_cells_txt, header=None, names=self.setting.columns), self.ko30,
                  on='sseqid', how='left')
    if len(df) == 0:
        logger.warning(f'No marker-like sequences found in file <{file.file}>.')
    else:
        if df['qseqid'].duplicated().sum() > 0:
            logger.warning('Duplicated sequences in cell number calculation.')
            df = df[~df['qseqid'].duplicated()]

        return df.groupby('ko30').apply(lambda x: sum(x['length'] / x['slen'])).sum() / 30