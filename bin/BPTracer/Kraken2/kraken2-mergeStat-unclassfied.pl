use File::Basename;
use Getopt::Long;
use FindBin qw($Bin);

my $Tax="$Bin/tax.list";

sub usage{
        print STDERR <<USAGE;
        Version 1.0 2018-07-12 by YaoYe
        Taxonmy Abundance Merge Table and Stat Pipeline.

        Options
                -prefix <s> : Required, the output prefix from step1
                -trim   <s> : the data summary for trim data (QC output)
                -out    <s> : output prefix
                -outdir <s> : Output Directory. Must be absolute path!!!
                -help       : show this help
USAGE
}

my ($prefix,$trim,$outdir,$out,$help);
GetOptions(
        "prefix:s"=>\$prefix,
        "outdir:s"=>\$outdir,
        "trim:s"=>\$trim,
        "out:s"=>\$out,
        "help"=>\$help,
);

if(!defined($prefix)||!defined($trim)||!defined ($out)){
        usage;
        exit;
}
$outdir||=`pwd`;chomp $outdir;

my ($line,@inf,%sample,%reads,%id,@tax);
open IA, "$trim" or die "can not open file: $trim\n";
open IB, "$prefix.D" or die "can not open file: $prefix.D\n";
open OA, ">$out.TaxStat.xls" or die "can not open file: $out.TaxStat.xls\n";
<IA>;
while($line=<IA>){
        chomp $line;    @inf=split /\s+/,$line; $sample{$inf[0]}=$inf[-2];
}
close IA;
$line=<IB>;chomp $line;@inf=split /\t/,$line;
for(my $i=3;$i<$#inf;$i+=2){
        $inf[$i]=~s/_num//;
        $id{$i}=$inf[$i];
}
while($line=<IB>){
        chomp $line;
        @inf=split /\t/,$line;
        push @tax,$inf[0];
        for(my $i=3;$i<$#inf;$i+=2){
                $reads{$i}{$inf[0]}=$inf[$i];
        }
}
close IB;
print OA "ID";$line=join("\t",@tax);
print OA "\t$line\tUnclassify\tTotalPairReads\n";
my (%unclass);
foreach my $i (sort {$a <=> $b} keys %reads){
        print OA "$id{$i}";
        my $uncl=$sample{$id{$i}};
        for(my $j=0;$j<=$#tax;$j++){
                print OA "\t$reads{$i}{$tax[$j]}";
                $uncl=$uncl-$reads{$i}{$tax[$j]};
        }
        printf OA "\t%ld\t$sample{$id{$i}}\n",$uncl;
        $unclass{$i}=$uncl;
}
close OA;

open IN, "$Tax" or die "can not open $Tax\n";
open OA, ">$out.table.tax.xls" or die "can not open $out.table\n";
my (%all,@item);
while($line=<IN>){
        chomp $line;
        push @item,$line;
        foreach my $i (keys %id){
                $all{$line}{$i}=0;
        }
}
close IN;

open IN, "$prefix.C" or die "can not open file $prefix.C\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/c__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.D" or die "can not open file $prefix.D\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/d__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.F" or die "can not open file $prefix.F\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/f__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.G" or die "can not open file $prefix.G\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/g__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.O" or die "can not open file $prefix.O\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/o__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.P" or die "can not open file $prefix.P\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/p__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

open IN, "$prefix.S" or die "can not open file $prefix.S\n";
<IN>;
while($line=<IN>){
        chomp $line;@inf=split /\t/,$line;
        my $temptax="";
        for(my $i=0;$i<=$#item;$i++){
                if($item[$i]=~/s__$inf[0]$/){
                        $temptax=$item[$i];
                        last;
                }
        }
        for(my $i=3;$i<$#inf;$i+=2){
                $all{$temptax}{$i}=$inf[$i];
        }
}
close IN;

print OA "ID";
foreach my $i (sort {$a<=>$b} keys %id){
        print OA "\t$id{$i}";
}
print OA "\tTaxonomy\n";
for(my $i=0;$i<$#item;$i++){
        print OA "Tax_$i";
        foreach my $j (sort {$a<=>$b} keys %id){
                print OA "\t$all{$item[$i]}{$j}";
        }
        print OA "\t$item[$i]\n";
}
print OA "Tax_Unclassified";
foreach my $i (sort {$a<=>$b} keys %id){
        print OA "\t$unclass{$i}";
}
print OA "\tUnclassified";
close OA;

open IN, "$out.table.tax.xls" or "can not open $out.table\n";
open OAD, ">$out.Archaea.D.xls";        open OAP, ">$out.Archaea.P.xls"; open OAC, ">$out.Archaea.C.xls";       open OAO, ">$out.Archaea.O.xls";
open OAF, ">$out.Archaea.F.xls";        open OAG, ">$out.Archaea.G.xls"; open OAS, ">$out.Archaea.S.xls";

open OBD, ">$out.Bacteria.D.xls";   open OBP, ">$out.Bacteria.P.xls"; open OBC, ">$out.Bacteria.C.xls";     open OBO, ">$out.Bacteria.O.xls";
open OBF, ">$out.Bacteria.F.xls";   open OBG, ">$out.Bacteria.G.xls"; open OBS, ">$out.Bacteria.S.xls";

open OED, ">$out.Eukaryota.D.xls";   open OEP, ">$out.Eukaryota.P.xls"; open OEC, ">$out.Eukaryota.C.xls";     open OEO, ">$out.Eukaryota.O.xls";
open OEF, ">$out.Eukaryota.F.xls";   open OEG, ">$out.Eukaryota.G.xls"; open OES, ">$out.Eukaryota.S.xls";

open OVoD, ">$out.Viroids.D.xls";   open OVoP, ">$out.Viroids.P.xls"; open OVoC, ">$out.Viroids.C.xls";     open OVoO, ">$out.Viroids.O.xls";
open OVoF, ">$out.Viroids.F.xls";   open OVoG, ">$out.Viroids.G.xls"; open OVoS, ">$out.Viroids.S.xls";

open OVuD, ">$out.Viruses.D.xls";   open OVuP, ">$out.Viruses.P.xls"; open OVuC, ">$out.Viruses.C.xls";     open OVuO, ">$out.Viruses.O.xls";
open OVuF, ">$out.Viruses.F.xls";   open OVuG, ">$out.Viruses.G.xls"; open OVuS, ">$out.Viruses.S.xls";


$line=<IN>;chomp $line;@inf=split /\t/,$line;   $line=join("\t",@inf[1..$#inf-1]);

print OAD "ID\t$line\n";print OAP "ID\t$line\n";print OAC "ID\t$line\n";print OAO "ID\t$line\n";print OAF "ID\t$line\n";print OAG "ID\t$line\n";print OAS "ID\t$line\n";
print OBD "ID\t$line\n";print OBP "ID\t$line\n";print OBC "ID\t$line\n";print OBO "ID\t$line\n";print OBF "ID\t$line\n";print OBG "ID\t$line\n";print OBS "ID\t$line\n";
print OED "ID\t$line\n";print OEP "ID\t$line\n";print OEC "ID\t$line\n";print OEO "ID\t$line\n";print OEF "ID\t$line\n";print OEG "ID\t$line\n";print OES "ID\t$line\n";
print OVoD "ID\t$line\n";print OVoP "ID\t$line\n";print OVoC "ID\t$line\n";print OVoO "ID\t$line\n";print OVoF "ID\t$line\n";print OVoG "ID\t$line\n";print OVoS "ID\t$line\n";
print OVuD "ID\t$line\n";print OVuP "ID\t$line\n";print OVuC "ID\t$line\n";print OVuO "ID\t$line\n";print OVuF "ID\t$line\n";print OVuG "ID\t$line\n";print OVuS "ID\t$line\n";

while($line=<IN>){
        chomp $line;
        @inf=split /\t/,$line;
        my $temp=0;
        for(my $i=1;$i<=$#inf;$i++){
                $temp+=$inf[$i];
        }
        next if ($temp==0);
        $temp=join("\t",@inf[1..$#inf-1]);
        my @ele=split /; /,$inf[-1];
        if($inf[-1]=~/^d__Archaea/){
                if($ele[$#ele]=~/s__/){
                        $ele[$#ele]=~s/s__//g;  print OAS "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/g__/){
                        $ele[$#ele]=~s/g__//g;  print OAG "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/f__/){
                        $ele[$#ele]=~s/f__//g;  print OAF "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/o__/){
                        $ele[$#ele]=~s/o__//g;  print OAO "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/c__/){
                        $ele[$#ele]=~s/c__//g;  print OAC "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/p__/){
                        $ele[$#ele]=~s/p__//g;  print OAP "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/d__/){
                        $ele[$#ele]=~s/d__//g;  print OAD "$ele[$#ele]\t$temp\n";
                }
        }
        if($inf[-1]=~/^d__Bacteria/){
                if($ele[$#ele]=~/s__/){
                        $ele[$#ele]=~s/s__//g;  print OBS "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/g__/){
                        $ele[$#ele]=~s/g__//g;  print OBG "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/f__/){
                        $ele[$#ele]=~s/f__//g;  print OBF "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/o__/){
                        $ele[$#ele]=~s/o__//g;  print OBO "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/c__/){
                        $ele[$#ele]=~s/c__//g;  print OBC "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/p__/){
                        $ele[$#ele]=~s/p__//g;  print OBP "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/d__/){
                        $ele[$#ele]=~s/d__//g;  print OBD "$ele[$#ele]\t$temp\n";
                }
        }
        if($inf[-1]=~/^d__Eukaryota/){
                if($ele[$#ele]=~/s__/){
                        $ele[$#ele]=~s/s__//g;  print OES "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/g__/){
                        $ele[$#ele]=~s/g__//g;  print OEG "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/f__/){
                        $ele[$#ele]=~s/f__//g;  print OEF "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/o__/){
                        $ele[$#ele]=~s/o__//g;  print OEO "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/c__/){
                        $ele[$#ele]=~s/c__//g;  print OEC "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/p__/){
                        $ele[$#ele]=~s/p__//g;  print OEP "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/d__/){
                        $ele[$#ele]=~s/d__//g;  print OED "$ele[$#ele]\t$temp\n";
                }
        }
        if($inf[-1]=~/^d__Viroids/){
                if($ele[$#ele]=~/s__/){
                        $ele[$#ele]=~s/s__//g;  print OVoS "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/g__/){
                        $ele[$#ele]=~s/g__//g;  print OVoG "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/f__/){
                        $ele[$#ele]=~s/f__//g;  print OVoF "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/o__/){
                        $ele[$#ele]=~s/o__//g;  print OVoO "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/c__/){
                        $ele[$#ele]=~s/c__//g;  print OVoC "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/p__/){
                        $ele[$#ele]=~s/p__//g;  print OVoP "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/d__/){
                        $ele[$#ele]=~s/d__//g;  print OVoD "$ele[$#ele]\t$temp\n";
                }
        }
        if($inf[-1]=~/^d__Viruses/){
                if($ele[$#ele]=~/s__/){
                        $ele[$#ele]=~s/s__//g;  print OVuS "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/g__/){
                        $ele[$#ele]=~s/g__//g;  print OVuG "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/f__/){
                        $ele[$#ele]=~s/f__//g;  print OVuF "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/o__/){
                        $ele[$#ele]=~s/o__//g;  print OVuO "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/c__/){
                        $ele[$#ele]=~s/c__//g;  print OVuC "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/p__/){
                        $ele[$#ele]=~s/p__//g;  print OVuP "$ele[$#ele]\t$temp\n";
                }
                elsif($ele[$#ele]=~/d__/){
                        $ele[$#ele]=~s/d__//g;  print OVuD "$ele[$#ele]\t$temp\n";
                }
        }
}
