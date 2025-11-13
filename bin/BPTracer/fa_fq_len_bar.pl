#!usr/bin/perl -w

use strict;
die "usage:perl $0 <fa or fq length> <output.pdf> <cut: contig or long>\n" unless @ARGV == 2 || @ARGV == 3;
if(@ARGV == 2){
	open O,">$ARGV[1].cmd.r";
	print O"a=read.table('$ARGV[0]');
pdf(file='$ARGV[1]',width=16,height=7);
hist(a[,2],breaks=50,main=\"Distribution of Length\",xlab=\"Length(bp)\",ylab=\"Density\",freq=FALSE,col='#E41A1C')
dev.off()\n";
`R --no-save < $ARGV[1].cmd.r`;
#`rm $ARGV[1].cmd.r`;
}
else{
	if($ARGV[2] eq "long"){
		open O,">$ARGV[1].cmd.r";
		print O"a=read.table('$ARGV[0]');
pdf(file='$ARGV[1]',width=16,height=7);
xtick1<-seq(0,40000,10000)
xtick2<-seq(0,40000,10000)
xtick2[5]<-'>=40000'
hist(a[,2],breaks=50,main='Distribution of Length',xlab='Length(bp)',ylab='Density',freq=FALSE,col='#E41A1C',xaxt='n')
axis(1, at=xtick1,labels=xtick2)
dev.off()\n";
`R --no-save < $ARGV[1].cmd.r`;
#`rm $ARGV[1].cmd.r`;
	}
	if($ARGV[2] eq "contig"){
                open O,">$ARGV[1].cmd.r";
                print O"a=read.table('$ARGV[0]');
pdf(file='$ARGV[1]',width=16,height=7);
xtick1<-seq(0,10000,2000)
xtick2<-seq(0,10000,2000)
xtick2[length(xtick1)]<-'>=10000'
hist(a[,2],breaks=50,main='Distribution of Length',xlab='Length(bp)',ylab='Density',freq=FALSE,col='#E41A1C',xaxt='n')
axis(1, at=xtick1,labels=xtick2)
dev.off()\n";
`R --no-save < $ARGV[1].cmd.r`;
#`rm $ARGV[1].cmd.r`;
	}
        if($ARGV[2] eq "gene"){
                open O,">$ARGV[1].cmd.r";
                print O"a=read.table('$ARGV[0]');
pdf(file='$ARGV[1]',width=16,height=7);
xtick1<-seq(0,5000,1000)
xtick2<-seq(0,5000,1000)
xtick2[length(xtick1)]<-'>=5000'
hist(a[,2],breaks=50,main='Distribution of Length',xlab='Length(bp)',ylab='Density',freq=FALSE,col='#E41A1C',xaxt='n')
axis(1, at=xtick1,labels=xtick2)
dev.off()\n";
`R --no-save < $ARGV[1].cmd.r`;
#`rm $ARGV[1].cmd.r`;
        }
}
